import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'locke_pets.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建分组颜色表
try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_colors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name VARCHAR(50) NOT NULL UNIQUE,
            color VARCHAR(20) NOT NULL DEFAULT '#6B7280',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("[OK] group_colors table created")
except Exception as e:
    print(f"[ERROR] group_colors table creation failed: {e}")

# 创建管理员账号表
try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("[OK] admin_accounts table created")
except Exception as e:
    print(f"[ERROR] admin_accounts table creation failed: {e}")

# 检查是否已有默认管理员账号
cursor.execute("SELECT COUNT(*) FROM admin_accounts")
count = cursor.fetchone()[0]

if count == 0:
    # 创建默认管理员账号
    cursor.execute(
        "INSERT INTO admin_accounts (username, password) VALUES (?, ?)",
        ("admin", "admin123")
    )
    print("[OK] Default admin account created: admin / admin123")
else:
    print(f"[INFO] Found {count} admin accounts, skip default creation")

conn.commit()
conn.close()
print("\n[DONE] Database migration completed!")
