"""
数据库独立迁移脚本
用法：python database_setup.py
该脚本管理所有表的创建和字段迁移，独立于 main.py 运行
"""
import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'system_data.db')

def run_migration():
    """执行所有数据库迁移"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}

    # ======== 已存在的表 ========

    if 'group_colors' not in existing_tables:
        cursor.execute('''
            CREATE TABLE group_colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name VARCHAR(50) NOT NULL UNIQUE,
                color VARCHAR(20) NOT NULL DEFAULT '#6B7280',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[迁移] group_colors 表已创建")

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
        print("[迁移] admin_accounts 表已创建")

    if 'pets' in existing_tables:
        cursor.execute("PRAGMA table_info(pets)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        for col, col_type in [('abilities', "TEXT DEFAULT '[]'"), ('is_active', 'BOOLEAN DEFAULT 1'), ('sort_order', 'INTEGER DEFAULT 0')]:
            if col not in existing_columns:
                cursor.execute("ALTER TABLE pets ADD COLUMN {} {}".format(col, col_type))
                print("[迁移] pets 表添加列: {}".format(col))

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
        print("[迁移] announcement 表已创建")

    if 'messages' not in existing_tables:
        cursor.execute('''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                avatar_index INTEGER DEFAULT 0,
                ip_address VARCHAR(50) DEFAULT '',
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[迁移] messages 表已创建")
    else:
        cursor.execute("PRAGMA table_info(messages)")
        msg_cols = {row[1] for row in cursor.fetchall()}
        if 'avatar_index' not in msg_cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN avatar_index INTEGER DEFAULT 0")
            print("[迁移] messages 表添加列: avatar_index")

    if 'message_avatars' not in existing_tables:
        cursor.execute('''
            CREATE TABLE message_avatars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url VARCHAR(255) NOT NULL,
                name VARCHAR(50) DEFAULT '自定义',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[迁移] message_avatars 表已创建")

    # ======== 新增表 ========

    # 1. site_config — 站点配置
    if 'site_config' not in existing_tables:
        cursor.execute('''
            CREATE TABLE site_config (
                key VARCHAR(100) PRIMARY KEY,
                value TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 插入默认配置
        default_configs = [
            ('site_title', '笑笑&屁屁-洛克王国世界'),
            ('site_subtitle', '异色精灵图鉴'),
            ('footer_text', '洛克王国异色精灵展示平台'),
            ('login_title', '洛克王国'),
            ('login_subtitle', '异色精灵管理系统'),
            ('login_visual_title', '和我一起探索洛克王国世界的精灵叭！'),
            ('login_visual_desc', '记录每一只独特的精灵，守护洛克王国的珍贵记忆'),
            ('login_footer', '屁屁的洛克王国精灵管理系统'),
            ('author_name', 'pipibigking'),
            ('project_name', '洛克王国异色精灵图鉴'),
            ('version', 'v1.0.0'),
            ('tech_stack', '前端：Vue 3 + TypeScript + Tailwind CSS + Vite\n后端：Python + FastAPI + SQLite\n部署：阿里云 ECS（CentOS 7.9）'),
            ('github_url', 'https://github.com/pipibigking'),
            ('email', '2807380340@qq.com'),
            ('qq', '196303221'),
            ('phone', '你的电话号码'),
            ('bg_home', '/images/bg/高举迪莫.jpg'),
            ('bg_pet_manage', '/images/bg/阿布星星蓝色.png'),
            ('bg_pet_manage_alt', '/images/bg/菊花梨五角星黄色.png'),
            ('bg_message_manage', '/images/bg/抹茶布丁绿色爱心.png'),
            ('bg_message_modal', '/images/bg/6炫彩鸭吉吉.jpg'),
            ('bg_account_manage', '/images/bg/小狮鹫蓝色云朵.png'),
            ('bg_announcement', '/images/bg/独角兽音符粉色.png'),
            ('bg_announcement_bar', '/images/bg/机械方方青色星星.jpg'),
            ('bg_admin_layout', '/images/bg/像素合照.jpg'),
        ]
        for key, value in default_configs:
            cursor.execute("INSERT OR IGNORE INTO site_config (key, value) VALUES (?, ?)", (key, value))
        print("[迁移] site_config 表已创建（含默认配置）")
    else:
        print("[迁移] site_config 表已存在")

    # 2. audit_logs — 审计日志
    if 'audit_logs' not in existing_tables:
        cursor.execute('''
            CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_user VARCHAR(50) DEFAULT '',
                action VARCHAR(50) NOT NULL,
                target_type VARCHAR(50) DEFAULT '',
                target_id INTEGER DEFAULT 0,
                detail TEXT DEFAULT '',
                ip_address VARCHAR(50) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[迁移] audit_logs 表已创建")
    else:
        print("[迁移] audit_logs 表已存在")

    # 3. uploaded_images — 上传图片记录（专门存储图片）
    if 'uploaded_images' not in existing_tables:
        cursor.execute('''
            CREATE TABLE uploaded_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL,
                original_name VARCHAR(255) DEFAULT '',
                url VARCHAR(255) NOT NULL,
                file_size INTEGER DEFAULT 0,
                file_type VARCHAR(50) DEFAULT '',
                width INTEGER DEFAULT 0,
                height INTEGER DEFAULT 0,
                uploaded_by VARCHAR(50) DEFAULT '',
                related_type VARCHAR(50) DEFAULT '',
                related_id INTEGER DEFAULT 0,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[迁移] uploaded_images 表已创建")
    else:
        cursor.execute("PRAGMA table_info(uploaded_images)")
        img_cols = {row[1] for row in cursor.fetchall()}
        for col, col_type in [
            ('width', 'INTEGER DEFAULT 0'),
            ('height', 'INTEGER DEFAULT 0'),
            ('is_deleted', 'BOOLEAN DEFAULT 0'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]:
            if col not in img_cols:
                cursor.execute("ALTER TABLE uploaded_images ADD COLUMN {} {}".format(col, col_type))
                print("[迁移] uploaded_images 表添加列: {}".format(col))
        print("[迁移] uploaded_images 表已存在，检查完成")

    # 4. price_history — 价格变更历史
    if 'price_history' not in existing_tables:
        cursor.execute('''
            CREATE TABLE price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                old_price INTEGER NOT NULL DEFAULT 0,
                new_price INTEGER NOT NULL DEFAULT 0,
                changed_by VARCHAR(50) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[迁移] price_history 表已创建")
    else:
        print("[迁移] price_history 表已存在")

    # 5. ip_blocks — IP 黑名单
    if 'ip_blocks' not in existing_tables:
        cursor.execute('''
            CREATE TABLE ip_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address VARCHAR(50) NOT NULL UNIQUE,
                reason VARCHAR(255) DEFAULT '',
                created_by VARCHAR(50) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[迁移] ip_blocks 表已创建")
    else:
        print("[迁移] ip_blocks 表已存在")

    conn.commit()
    conn.close()
    print("[迁移] 全部迁移完成！")

if __name__ == "__main__":
    run_migration()
