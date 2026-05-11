from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(current_dir, 'locke_pets.db')}"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="洛克王国精灵展示 API", version="1.0")

@app.get("/")
def root():
    return {"message": "洛克王国异色精灵展示 API", "docs": "/docs", "api": "/api/pets"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

project_dir = os.path.dirname(current_dir)
images_dir = os.path.join(project_dir, "images")
icons_dir = os.path.join(project_dir, "wiki_style_icons")

if os.path.exists(images_dir):
    app.mount("/images", StaticFiles(directory=images_dir), name="images")
    print(f"图片目录已挂载: {images_dir}")
else:
    print(f"警告: 图片目录不存在: {images_dir}")

if os.path.exists(icons_dir):
    app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")
    print(f"属性图标目录已挂载: {icons_dir}")
else:
    print(f"警告: 属性图标目录不存在: {icons_dir}")

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
                "is_active": pet.is_active
            })

    valid_sort_fields = ["id", "price", "name"]
    if sort_by not in valid_sort_fields:
        sort_by = "price"

    if sort_order == "desc":
        result.sort(key=lambda x: x[sort_by], reverse=True)
    else:
        result.sort(key=lambda x: x[sort_by])

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
        "is_active": pet.is_active
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
def create_pet(body: PetCreate):
    db = SessionLocal()
    pet = Pet(
        name=body.name,
        group=body.group,
        image_url=body.image_url,
        price=body.price,
        attributes=json.dumps(body.attributes, ensure_ascii=False),
        description=body.description,
        abilities=json.dumps(body.abilities, ensure_ascii=False) if body.abilities else "[]",
        is_active=True
    )
    db.add(pet)
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
        "created_at": str(pet.created_at) if pet.created_at else None
    }
    db.close()
    return result


@app.put("/api/pets/{pet_id}")
def update_pet(pet_id: int, body: PetUpdate):
    db = SessionLocal()
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        db.close()
        raise HTTPException(status_code=404, detail="精灵不存在")

    update_data = body.dict(exclude_unset=True)
    if "attributes" in update_data:
        update_data["attributes"] = json.dumps(update_data["attributes"], ensure_ascii=False)
    if "abilities" in update_data:
        update_data["abilities"] = json.dumps(update_data["abilities"], ensure_ascii=False)

    for key, value in update_data.items():
        setattr(pet, key, value)

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
        "created_at": str(pet.created_at) if pet.created_at else None
    }
    db.close()
    return result


@app.delete("/api/pets/{pet_id}")
def delete_pet(pet_id: int):
    db = SessionLocal()
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        db.close()
        raise HTTPException(status_code=404, detail="精灵不存在")

    db.delete(pet)
    db.commit()
    db.close()
    return {"message": "删除成功"}


@app.patch("/api/pets/{pet_id}/toggle-active")
def toggle_active(pet_id: int):
    db = SessionLocal()
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        db.close()
        raise HTTPException(status_code=404, detail="精灵不存在")

    pet.is_active = not pet.is_active
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
        "created_at": str(pet.created_at) if pet.created_at else None
    }
    db.close()
    return result


@app.patch("/api/pets/batch-activate")
def batch_activate():
    db = SessionLocal()
    count = db.query(Pet).filter(Pet.is_active == False).update({"is_active": True})
    db.commit()
    db.close()
    return {"message": f"已上架 {count} 只精灵", "count": count}


@app.patch("/api/pets/batch-deactivate")
def batch_deactivate():
    db = SessionLocal()
    count = db.query(Pet).filter(Pet.is_active == True).update({"is_active": False})
    db.commit()
    db.close()
    return {"message": f"已下架 {count} 只精灵", "count": count}


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
        return {
            "success": True,
            "username": account.username,
            "message": "登录成功"
        }
    else:
        raise HTTPException(status_code=401, detail="账号或密码错误")


def auto_migrate():
    """自动创建缺失的表和列"""
    import sqlite3
    
    db_path = os.path.join(current_dir, 'locke_pets.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    if 'group_colors' not in existing_tables:
        cursor.execute('''
            CREATE TABLE group_colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name VARCHAR(50) NOT NULL UNIQUE,
                color VARCHAR(20) NOT NULL DEFAULT '#6B7280',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[Migration] group_colors table created")
    
    if 'admin_accounts' not in existing_tables:
        cursor.execute('''
            CREATE TABLE admin_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[Migration] admin_accounts table created")
    
    if 'pets' in existing_tables:
        cursor.execute("PRAGMA table_info(pets)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        if 'abilities' not in existing_columns:
            cursor.execute("ALTER TABLE pets ADD COLUMN abilities TEXT DEFAULT '[]'")
            print("[Migration] abilities column added to pets table")
        
        if 'is_active' not in existing_columns:
            cursor.execute("ALTER TABLE pets ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("[Migration] is_active column added to pets table")
    
    if 'announcement' not in existing_tables:
        cursor.execute('''
            CREATE TABLE announcement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute(
            "INSERT INTO announcement (content) VALUES (?)",
            ('欢迎来到笑笑屁屁-洛克王国异色精灵交易平台！新精灵即将上架，敬请期待~',)
        )
        print("[Migration] announcement table created")
    
    conn.commit()
    conn.close()
    print("[Migration] Auto-migration completed")


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


if __name__ == "__main__":
    import uvicorn
    
    auto_migrate()
    
    init_default_data()
    
    uvicorn.run(app, host="0.0.0.0", port=8004)