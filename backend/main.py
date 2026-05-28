from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query, Body, Request, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
import json
import secrets

# ======== JWT 认证配置 ========
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

current_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = "sqlite:///" + os.path.join(current_dir, 'system_data.db')

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="洛克王国精灵展示 API", version="1.0")

project_dir = os.path.dirname(current_dir)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======== API 认证中间件 ========
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method

    # 登录和验证接口不需要认证
    if path == "/api/admin/login" or path == "/api/admin/verify":
        return await call_next(request)

    # 管理端路径（/api/admin/*）需要认证
    if path.startswith("/api/admin/"):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "未提供有效的认证凭证"})
        token = auth_header.split(" ", 1)[1]
        payload = verify_access_token(token)
        if payload is None:
            return JSONResponse(status_code=401, content={"detail": "Token 无效或已过期"})
        request.state.admin_user = payload.get("sub")
        return await call_next(request)

    # 非管理端的写入操作（POST/PUT/PATCH/DELETE）需要认证
    if method in ("POST", "PUT", "PATCH", "DELETE"):
        # 公开发布留言不需要认证
        if path == "/api/messages" and method == "POST":
            return await call_next(request)
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "未提供有效的认证凭证"})
        token = auth_header.split(" ", 1)[1]
        payload = verify_access_token(token)
        if payload is None:
            return JSONResponse(status_code=401, content={"detail": "Token 无效或已过期"})
        request.state.admin_user = payload.get("sub")

    return await call_next(request)


images_dir = os.path.join(project_dir, "images")
icons_dir = os.path.join(project_dir, "wiki_style_icons")

if os.path.exists(images_dir):
    app.mount("/images", StaticFiles(directory=images_dir), name="images")
    print("图片目录已挂载: {}".format(images_dir))
else:
    print("警告: 图片目录不存在: {}".format(images_dir))

uploads_dir = os.path.join(project_dir, "images", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/images/uploads", StaticFiles(directory=uploads_dir), name="images_uploads")

if os.path.exists(icons_dir):
    app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")
    print("属性图标目录已挂载: {}".format(icons_dir))
else:
    print("警告: 属性图标目录不存在: {}".format(icons_dir))

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    group = Column(String(50), nullable=False)
    image_url = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    attributes = Column(Text, default="[]")
    description = Column(Text, default="")
    abilities = Column(Text, default="[]")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

class Announcement(Base):
    __tablename__ = "announcement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, default="")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class GroupColor(Base):
    __tablename__ = "group_colors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(50), nullable=False, unique=True)
    color = Column(String(20), nullable=False, default="#6B7280")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AdminAccount(Base):
    __tablename__ = "admin_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    avatar_index = Column(Integer, default=0)
    ip_address = Column(String(50), default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class MessageAvatar(Base):
    __tablename__ = "message_avatars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    name = Column(String(50), default="自定义")
    created_at = Column(DateTime, default=func.now())


# ======== 新增表模型 ========

class SiteConfig(Base):
    __tablename__ = "site_config"
    key = Column(String(100), primary_key=True)
    value = Column(Text, default="")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_user = Column(String(50), default="")
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), default="")
    target_id = Column(Integer, default=0)
    detail = Column(Text, default="")
    ip_address = Column(String(50), default="")
    created_at = Column(DateTime, default=func.now())

class UploadedImage(Base):
    __tablename__ = "uploaded_images"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), default="")
    url = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String(50), default="")
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    uploaded_by = Column(String(50), default="")
    related_type = Column(String(50), default="")
    related_id = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, nullable=False)
    old_price = Column(Integer, nullable=False, default=0)
    new_price = Column(Integer, nullable=False, default=0)
    changed_by = Column(String(50), default="")
    created_at = Column(DateTime, default=func.now())

class IpBlock(Base):
    __tablename__ = "ip_blocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False, unique=True)
    reason = Column(String(255), default="")
    created_by = Column(String(50), default="")
    created_at = Column(DateTime, default=func.now())


# ======== 审计日志辅助函数 ========

def add_audit_log(db, admin_user, action, target_type="", target_id=0, detail="", ip_address=""):
    log = AuditLog(
        admin_user=admin_user,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip_address
    )
    db.add(log)

def add_price_history(db, pet_id, old_price, new_price, changed_by=""):
    record = PriceHistory(
        pet_id=pet_id,
        old_price=old_price,
        new_price=new_price,
        changed_by=changed_by
    )
    db.add(record)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/pets")
def get_pets(
    group: str = Query(None, description="分组筛选"),
    search: str = Query(None, description="搜索关键词"),
    sort_by: str = Query("price", description="排序字段"),
    sort_order: str = Query("asc", description="排序方向"),
    attribute: str = Query(None, description="属性筛选"),
    include_inactive: bool = Query(False, description="是否包含已下架精灵")
):
    db = SessionLocal()
    query = db.query(Pet)
    if not include_inactive:
        query = query.filter(Pet.is_active == True)
    pets = query.all()

    result = []
    for pet in pets:
        try:
            attrs = json.loads(pet.attributes)
        except:
            attrs = []
        
        match = True
        
        if group and pet.group != group:
            match = False
        
        if match and search and search.lower() not in pet.name.lower():
            match = False
        
        if match and attribute:
            if attribute not in attrs:
                match = False
        
        if match:
            result.append({
                "id": pet.id,
                "name": pet.name,
                "group": pet.group,
                "image_url": pet.image_url,
                "price": pet.price,
                "attributes": attrs,
                "description": pet.description,
                "abilities": json.loads(pet.abilities) if pet.abilities else [],
                "is_active": pet.is_active,
                "sort_order": pet.sort_order
            })

    valid_sort_fields = ["id", "price", "name", "sort_order"]
    if sort_by not in valid_sort_fields:
        sort_by = "price"

    if sort_order == "desc":
        result.sort(key=lambda x: x[sort_by], reverse=True)
    else:
        result.sort(key=lambda x: x[sort_by])

    result.sort(key=lambda x: x.get("sort_order", 0))

    db.close()
    return result

@app.get("/api/pets/{pet_id}")
def get_pet(pet_id: int):
    db = SessionLocal()
    pet = db.query(Pet).filter(Pet.id == pet_id).first()

    if not pet:
        raise HTTPException(status_code=404, detail="精灵不存在")

    result = {
        "id": pet.id,
        "name": pet.name,
        "group": pet.group,
        "image_url": pet.image_url,
        "price": pet.price,
        "attributes": json.loads(pet.attributes),
        "description": pet.description,
        "abilities": json.loads(pet.abilities) if pet.abilities else [],
        "is_active": pet.is_active,
        "sort_order": pet.sort_order
    }

    db.close()
    return result

@app.get("/api/groups")
def get_groups():
    db = SessionLocal()
    groups = db.query(Pet.group).distinct().all()
    result = [group[0] for group in groups]
    db.close()
    return result


class PetCreate(BaseModel):
    name: str
    group: str
    image_url: str
    price: int
    attributes: list = []
    description: str = ""
    abilities: list = []
    is_active: bool = True


class PetUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[int] = None
    attributes: Optional[list] = None
    description: Optional[str] = None
    abilities: Optional[list] = None
    is_active: Optional[bool] = None


class AnnouncementBody(BaseModel):
    content: str


@app.post("/api/pets")
def create_pet(body: PetCreate, request: Request = None):
    db = SessionLocal()
    pet = Pet(
        name=body.name,
        group=body.group,
        image_url=body.image_url,
        price=body.price,
        attributes=json.dumps(body.attributes, ensure_ascii=False),
        description=body.description,
        abilities=json.dumps(body.abilities, ensure_ascii=False) if body.abilities else "[]",
        is_active=body.is_active
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    add_audit_log(db, request.headers.get("x-admin-user", "") if request else "", "create_pet", "pet", pet.id,
                   "创建精灵：{}".format(pet.name))
    db.commit()
    result = {
        "id": pet.id,
        "name": pet.name,
        "group": pet.group,
        "image_url": pet.image_url,
        "price": pet.price,
        "attributes": json.loads(pet.attributes),
        "description": pet.description,
        "abilities": json.loads(pet.abilities) if pet.abilities else [],
        "is_active": pet.is_active,
        "sort_order": pet.sort_order,
        "created_at": str(pet.created_at) if pet.created_at else None
    }
    db.close()
    return result


@app.put("/api/pets/sort-order")
async def batch_update_sort_order(request: Request):
    import json as _json
    raw_bytes = await request.body()
    data = _json.loads(raw_bytes)
    items = data.get("items", [])
    db = SessionLocal()
    count = 0
    for item in items:
        try:
            pet_id = int(item.get("id", 0))
            sort_val = int(item.get("sort_order", 0))
            pet = db.query(Pet).filter(Pet.id == pet_id).first()
            if pet:
                pet.sort_order = sort_val
                count += 1
        except (ValueError, TypeError, AttributeError):
            continue
    db.commit()
    db.close()
    return {"message": "已更新 {} 只精灵的排序".format(count), "count": count}


@app.put("/api/pets/{pet_id}")
def update_pet(pet_id: int, body: PetUpdate, request: Request = None):
    db = SessionLocal()
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        db.close()
        raise HTTPException(status_code=404, detail="精灵不存在")

    old_price = pet.price
    update_data = body.dict(exclude_unset=True)
    if "attributes" in update_data:
        update_data["attributes"] = json.dumps(update_data["attributes"], ensure_ascii=False)
    if "abilities" in update_data:
        update_data["abilities"] = json.dumps(update_data["abilities"], ensure_ascii=False)

    for key, value in update_data.items():
        setattr(pet, key, value)

    if "price" in update_data and update_data["price"] != old_price:
        add_price_history(db, pet_id, old_price, update_data["price"])
        add_audit_log(db, request.headers.get("x-admin-user", "") if request else "", "update_price", "pet", pet_id,
                       "价格 {} → {}".format(old_price, update_data["price"]))

    db.commit()
    db.refresh(pet)
    result = {
        "id": pet.id,
        "name": pet.name,
        "group": pet.group,
        "image_url": pet.image_url,
        "price": pet.price,
        "attributes": json.loads(pet.attributes),
        "description": pet.description,
        "abilities": json.loads(pet.abilities) if pet.abilities else [],
        "is_active": pet.is_active,
        "sort_order": pet.sort_order,
        "created_at": str(pet.created_at) if pet.created_at else None
    }
    db.close()
    return result


@app.delete("/api/pets/{pet_id}")
def delete_pet(pet_id: int, request: Request = None):
    db = SessionLocal()
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        db.close()
        raise HTTPException(status_code=404, detail="精灵不存在")

    pet_name = pet.name
    db.delete(pet)
    add_audit_log(db, request.headers.get("x-admin-user", "") if request else "", "delete_pet", "pet", pet_id,
                   "删除精灵：{}".format(pet_name))
    db.commit()
    db.close()
    return {"message": "删除成功"}


@app.patch("/api/pets/{pet_id}/toggle-active")
def toggle_active(pet_id: int, request: Request = None):
    db = SessionLocal()
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        db.close()
        raise HTTPException(status_code=404, detail="精灵不存在")

    pet.is_active = not pet.is_active
    status_text = "上架" if pet.is_active else "下架"
    add_audit_log(db, request.headers.get("x-admin-user", "") if request else "", "toggle_active", "pet", pet_id,
                   "{} → {}".format(pet.name, status_text))
    db.commit()
    db.refresh(pet)
    result = {
        "id": pet.id,
        "name": pet.name,
        "group": pet.group,
        "image_url": pet.image_url,
        "price": pet.price,
        "attributes": json.loads(pet.attributes),
        "description": pet.description,
        "abilities": json.loads(pet.abilities) if pet.abilities else [],
        "is_active": pet.is_active,
        "sort_order": pet.sort_order,
        "created_at": str(pet.created_at) if pet.created_at else None
    }
    db.close()
    return result


@app.patch("/api/pets/batch-activate")
def batch_activate():
    db = SessionLocal()
    count = db.query(Pet).filter(Pet.is_active == False, (Pet.group != '草稿')).update({"is_active": True})
    db.commit()
    db.close()
    return {"message": "已上架 {} 只精灵".format(count), "count": count}


@app.patch("/api/pets/batch-deactivate")
def batch_deactivate():
    db = SessionLocal()
    count = db.query(Pet).filter(Pet.is_active == True, (Pet.group != '草稿')).update({"is_active": False})
    db.commit()
    db.close()
    return {"message": "已下架 {} 只精灵".format(count), "count": count}


@app.get("/api/announcement")
def get_announcement():
    db = SessionLocal()
    announcement = db.query(Announcement).first()
    db.close()
    if not announcement:
        return {"id": 0, "content": "", "updated_at": ""}
    return {
        "id": announcement.id,
        "content": announcement.content,
        "updated_at": str(announcement.updated_at) if announcement.updated_at else ""
    }


@app.put("/api/announcement")
def update_announcement(body: AnnouncementBody):
    db = SessionLocal()
    announcement = db.query(Announcement).first()
    if announcement:
        announcement.content = body.content
    else:
        announcement = Announcement(content=body.content)
        db.add(announcement)
    db.commit()
    db.refresh(announcement)
    result = {
        "id": announcement.id,
        "content": announcement.content,
        "updated_at": str(announcement.updated_at) if announcement.updated_at else ""
    }
    db.close()
    return result


class GroupColorUpdate(BaseModel):
    color: str

class AdminAccountCreate(BaseModel):
    username: str
    password: str

class AdminAccountUpdate(BaseModel):
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/api/group-colors")
def get_group_colors():
    db = SessionLocal()
    colors = db.query(GroupColor).all()
    result = {c.group_name: c.color for c in colors}
    db.close()
    return result


@app.put("/api/group-colors/{group_name}")
def update_group_color(group_name: str, body: GroupColorUpdate):
    db = SessionLocal()
    color_record = db.query(GroupColor).filter(GroupColor.group_name == group_name).first()
    if color_record:
        color_record.color = body.color
    else:
        color_record = GroupColor(group_name=group_name, color=body.color)
        db.add(color_record)
    db.commit()
    db.refresh(color_record)
    result = {
        "group_name": color_record.group_name,
        "color": color_record.color,
        "updated_at": str(color_record.updated_at) if color_record.updated_at else ""
    }
    db.close()
    return result


class GroupRename(BaseModel):
    new_name: str


@app.put("/api/groups/{group_name}")
def rename_group(group_name: str, body: GroupRename):
    db = SessionLocal()
    new_name = body.new_name.strip()
    if not new_name:
        db.close()
        raise HTTPException(status_code=400, detail="新名称不能为空")
    
    updated = db.query(Pet).filter(Pet.group == group_name).update({"group": new_name})
    
    color_record = db.query(GroupColor).filter(GroupColor.group_name == group_name).first()
    if color_record:
        target_color = db.query(GroupColor).filter(GroupColor.group_name == new_name).first()
        if target_color:
            target_color.color = color_record.color
            db.delete(color_record)
        else:
            color_record.group_name = new_name
    
    db.commit()
    db.close()
    return {"message": "已将 {} 只精灵从 '{}' 移至 '{}'".format(updated, group_name, new_name), "old_name": group_name, "new_name": new_name}



@app.get("/api/admin/accounts")
def get_admin_accounts():
    db = SessionLocal()
    accounts = db.query(AdminAccount).all()
    result = [
        {
            "id": acc.id,
            "username": acc.username,
            "created_at": str(acc.created_at) if acc.created_at else "",
            "updated_at": str(acc.updated_at) if acc.updated_at else ""
        }
        for acc in accounts
    ]
    db.close()
    return result


@app.post("/api/admin/accounts")
def create_admin_account(body: AdminAccountCreate):
    db = SessionLocal()
    existing = db.query(AdminAccount).filter(AdminAccount.username == body.username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="账号已存在")
    
    account = AdminAccount(username=body.username, password=body.password)
    db.add(account)
    db.commit()
    db.refresh(account)
    result = {
        "id": account.id,
        "username": account.username,
        "created_at": str(account.created_at) if account.created_at else "",
        "updated_at": str(account.updated_at) if account.updated_at else ""
    }
    db.close()
    return result


@app.put("/api/admin/accounts/{username}")
def update_admin_account(username: str, body: AdminAccountUpdate):
    db = SessionLocal()
    account = db.query(AdminAccount).filter(AdminAccount.username == username).first()
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="账号不存在")
    
    account.password = body.password
    db.commit()
    db.refresh(account)
    result = {
        "id": account.id,
        "username": account.username,
        "updated_at": str(account.updated_at) if account.updated_at else ""
    }
    db.close()
    return result


@app.delete("/api/admin/accounts/{username}")
def delete_admin_account(username: str):
    db = SessionLocal()
    account = db.query(AdminAccount).filter(AdminAccount.username == username).first()
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="账号不存在")
    
    # 检查是否至少保留一个账号
    count = db.query(AdminAccount).count()
    if count <= 1:
        db.close()
        raise HTTPException(status_code=400, detail="至少保留一个管理员账号")
    
    db.delete(account)
    db.commit()
    db.close()
    return {"message": "删除成功"}


@app.post("/api/admin/login")
def admin_login(body: LoginRequest):
    db = SessionLocal()
    account = db.query(AdminAccount).filter(
        AdminAccount.username == body.username,
        AdminAccount.password == body.password
    ).first()
    db.close()
    
    if account:
        token = create_access_token({"sub": account.username})
        return {
            "success": True,
            "token": token,
            "username": account.username,
            "message": "登录成功"
        }
    else:
        raise HTTPException(status_code=401, detail="账号或密码错误")


@app.get("/api/admin/verify")
def verify_token(request: Request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证凭证")
    token = auth_header.split(" ", 1)[1]
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    return {"valid": True, "username": payload.get("sub")}


class MessageCreate(BaseModel):
    nickname: str
    content: str
    avatar_index: int = 0


@app.get("/api/messages")
def get_messages(include_read: bool = Query(True, description="是否包含已读留言")):
    db = SessionLocal()
    query = db.query(Message).order_by(Message.created_at.desc())
    if not include_read:
        query = query.filter(Message.is_read == False)
    messages = query.all()
    result = [
        {
            "id": m.id,
            "nickname": m.nickname,
            "content": m.content,
            "avatar_index": m.avatar_index if m.avatar_index is not None else 0,
            "is_read": m.is_read,
            "created_at": str(m.created_at) if m.created_at else ""
        }
        for m in messages
    ]
    db.close()
    return result


@app.get("/api/messages/unread-count")
def get_unread_count():
    db = SessionLocal()
    count = db.query(Message).filter(Message.is_read == False).count()
    db.close()
    return {"count": count}


@app.post("/api/messages")
def create_message(body: MessageCreate, request: Request):
    if not body.nickname.strip() or not body.content.strip():
        raise HTTPException(status_code=400, detail="昵称和内容不能为空")
    
    db = SessionLocal()
    client_ip = request.client.host if request.client else "unknown"
    
    from datetime import datetime, timedelta
    one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
    recent = db.query(Message).filter(
        Message.ip_address == client_ip,
        Message.created_at >= one_minute_ago
    ).first()
    
    if recent:
        db.close()
        raise HTTPException(status_code=429, detail="留言过于频繁，请1分钟后再试")
    
    message = Message(
        nickname=body.nickname.strip(),
        content=body.content.strip(),
        avatar_index=body.avatar_index,
        ip_address=client_ip,
        is_read=False
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    result = {
        "id": message.id,
        "nickname": message.nickname,
        "content": message.content,
        "avatar_index": message.avatar_index if message.avatar_index is not None else 0,
        "is_read": message.is_read,
        "created_at": str(message.created_at) if message.created_at else ""
    }
    db.close()
    return result


@app.put("/api/messages/{message_id}/read")
def mark_message_read(message_id: int):
    db = SessionLocal()
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        db.close()
        raise HTTPException(status_code=404, detail="留言不存在")
    message.is_read = True
    db.commit()
    db.close()
    return {"message": "已标记为已读"}


@app.put("/api/messages/read-all")
def mark_all_read():
    db = SessionLocal()
    db.query(Message).filter(Message.is_read == False).update({"is_read": True})
    db.commit()
    db.close()
    return {"message": "全部标记为已读"}


@app.delete("/api/messages/{message_id}")
def delete_message(message_id: int, request: Request = None):
    db = SessionLocal()
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        db.close()
        raise HTTPException(status_code=404, detail="留言不存在")
    add_audit_log(db, request.headers.get("x-admin-user", "") if request else "", "delete_message", "message", message_id,
                   "删除留言：{}...".format(message.content[:20] if message.content else ""))
    db.delete(message)
    db.commit()
    db.close()
    return {"message": "删除成功"}


BUILTIN_AVATARS = [
    {"id": -1, "name": "迪莫", "url": "/images/avatar/迪莫.jpg"},
    {"id": -2, "name": "火花", "url": "/images/avatar/火花.jpg"},
    {"id": -3, "name": "菊花梨", "url": "/images/avatar/菊花梨.jpg"},
    {"id": -4, "name": "喵喵", "url": "/images/avatar/喵喵.jpg"},
    {"id": -5, "name": "水蓝蓝", "url": "/images/avatar/水蓝蓝.jpg"},
    {"id": -6, "name": "鸭吉吉", "url": "/images/avatar/鸭吉吉.jpg"}
]

@app.get("/api/message-avatars")
def get_message_avatars():
    db = SessionLocal()
    try:
        custom = db.query(MessageAvatar).order_by(MessageAvatar.id).all()
        custom_list = [{"id": a.id, "name": a.name, "url": a.url} for a in custom]
    finally:
        db.close()
    return {"builtin": BUILTIN_AVATARS, "custom": custom_list}

@app.post("/api/message-avatars/upload")
async def upload_message_avatar(file: UploadFile = File(...), name: str = ""):
    import uuid, shutil, os as _os
    ext = os.path.splitext(file.filename or "avatar.png")[1] or ".png"
    raw_name = os.path.splitext(os.path.basename(file.filename or "自定义"))[0]
    avatar_name = name if name else raw_name
    filename = "avatar_{}{}".format(uuid.uuid4().hex[:8], ext)
    uploads_dir = os.path.join(os.path.dirname(current_dir), "images", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    url = "/images/uploads/{}".format(filename)
    db = SessionLocal()
    try:
        avatar = MessageAvatar(url=url, name=avatar_name)
        db.add(avatar)
        db.commit()
        db.refresh(avatar)
        return {"id": avatar.id, "name": avatar.name, "url": avatar.url}
    finally:
        db.close()

@app.delete("/api/message-avatars/{avatar_id}")
def delete_message_avatar(avatar_id: int):
    db = SessionLocal()
    try:
        avatar = db.query(MessageAvatar).filter(MessageAvatar.id == avatar_id).first()
        if not avatar:
            raise HTTPException(status_code=404, detail="头像不存在")
        db.delete(avatar)
        db.commit()
        return {"message": "删除成功"}
    finally:
        db.close()


# ======== Site Config API ========

@app.get("/api/site-config")
def get_site_config():
    db = SessionLocal()
    try:
        configs = db.query(SiteConfig).all()
        return {c.key: c.value for c in configs}
    finally:
        db.close()

@app.put("/api/site-config")
def update_site_config(body: dict = Body(...)):
    db = SessionLocal()
    try:
        for key, value in body.items():
            existing = db.query(SiteConfig).filter(SiteConfig.key == key).first()
            if existing:
                existing.value = value
            else:
                db.add(SiteConfig(key=key, value=value))
        db.commit()
        return {"message": "保存成功"}
    finally:
        db.close()


# ======== Audit Log API ========

@app.get("/api/audit-logs")
def get_audit_logs(limit: int = Query(50), offset: int = Query(0)):
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
        return [
            {
                "id": log.id,
                "admin_user": log.admin_user,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "created_at": str(log.created_at) if log.created_at else ""
            }
            for log in logs
        ]
    finally:
        db.close()


# ======== Price History API ========

@app.get("/api/price-history/{pet_id}")
def get_price_history(pet_id: int):
    db = SessionLocal()
    try:
        records = db.query(PriceHistory).filter(PriceHistory.pet_id == pet_id).order_by(PriceHistory.created_at.desc()).limit(20).all()
        return [
            {
                "id": r.id,
                "old_price": r.old_price,
                "new_price": r.new_price,
                "changed_by": r.changed_by,
                "created_at": str(r.created_at) if r.created_at else ""
            }
            for r in records
        ]
    finally:
        db.close()


# ======== IP Block API ========

@app.get("/api/ip-blocks")
def get_ip_blocks():
    db = SessionLocal()
    try:
        blocks = db.query(IpBlock).all()
        return [
            {"id": b.id, "ip_address": b.ip_address, "reason": b.reason, "created_by": b.created_by, "created_at": str(b.created_at) if b.created_at else ""}
            for b in blocks
        ]
    finally:
        db.close()

@app.post("/api/ip-blocks")
def create_ip_block(body: dict = Body(...)):
    ip = body.get("ip_address", "").strip()
    reason = body.get("reason", "")
    if not ip:
        raise HTTPException(status_code=400, detail="IP地址不能为空")
    db = SessionLocal()
    try:
        existing = db.query(IpBlock).filter(IpBlock.ip_address == ip).first()
        if existing:
            raise HTTPException(status_code=409, detail="该IP已在黑名单中")
        block = IpBlock(ip_address=ip, reason=reason, created_by=body.get("created_by", ""))
        db.add(block)
        db.commit()
        return {"message": "添加成功"}
    finally:
        db.close()

@app.delete("/api/ip-blocks/{block_id}")
def delete_ip_block(block_id: int):
    db = SessionLocal()
    try:
        block = db.query(IpBlock).filter(IpBlock.id == block_id).first()
        if not block:
            raise HTTPException(status_code=404, detail="记录不存在")
        db.delete(block)
        db.commit()
        return {"message": "删除成功"}
    finally:
        db.close()


@app.post("/api/upload")
async def upload_pet_image(file: UploadFile = File(...), request: Request = None):
    import uuid
    import shutil
    
    ext = os.path.splitext(file.filename or "image.png")[1] or ".png"
    filename = "{}{}".format(uuid.uuid4().hex, ext)
    
    uploads_dir = os.path.join(os.path.dirname(current_dir), "images", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    file_path = os.path.join(uploads_dir, filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    width, height = 0, 0
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            width, height = img.size
    except:
        pass
    
    file_size = os.path.getsize(file_path)
    url = "/images/uploads/{}".format(filename)
    
    db = SessionLocal()
    try:
        uploaded_image = UploadedImage(
            filename=filename,
            original_name=file.filename or "",
            url=url,
            file_size=file_size,
            file_type=file.content_type or "",
            width=width,
            height=height,
            uploaded_by=request.headers.get("x-admin-user", "") if request else "",
            related_type="pet",
            related_id=0
        )
        db.add(uploaded_image)
        db.commit()
        db.refresh(uploaded_image)
    finally:
        db.close()
    
    return {
        "id": uploaded_image.id if 'uploaded_image' in dir() else None,
        "url": url,
        "filename": filename,
        "file_size": file_size,
        "width": width,
        "height": height,
        "file_type": file.content_type or ""
    }


def auto_migrate():
    """自动创建缺失的表和列，委托给 database_setup.py"""
    from database_setup import run_migration
    run_migration()


def init_default_data():
    """初始化默认数据"""
    db = SessionLocal()
    
    admin_count = db.query(AdminAccount).count()
    if admin_count == 0:
        default_admin = AdminAccount(username="admin", password="admin123")
        db.add(default_admin)
        print("已创建默认管理员账号: admin / admin123")
    
    db.commit()
    db.close()


frontend_dist = os.path.join(project_dir, "frontend", "dist")
assets_dir = os.path.join(frontend_dist, "assets")

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    print("[Deploy] 前端资源目录已加载: {}".format(assets_dir))

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    print("[Deploy] 前端静态文件已加载: {}".format(frontend_dist))
    print("[Deploy] 访问 http://localhost:8004/ 打开前端页面")
else:
    print("[Deploy] 警告: 前端构建目录不存在: {}".format(frontend_dist))
    print("[Deploy] 请先在 frontend 目录执行: npm run build")


if __name__ == "__main__":
    import uvicorn
    
    auto_migrate()
    
    init_default_data()
    
    print("\n{}".format('='*50))
    print("  洛克王国异色精灵展示系统")
    print("  API 文档: http://localhost:8004/docs")
    print("  前端页面: http://localhost:8004/")
    print("{}\n".format('='*50))
    
    uvicorn.run(app, host="0.0.0.0", port=8004)