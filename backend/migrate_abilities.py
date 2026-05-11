import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'locke_pets.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT abilities FROM pets LIMIT 1")
    print("abilities 字段已存在")
except sqlite3.OperationalError:
    print("正在添加 abilities 字段...")
    cursor.execute("ALTER TABLE pets ADD COLUMN abilities TEXT DEFAULT '[]'")
    conn.commit()
    print("abilities 字段添加成功")

conn.close()
print("数据库迁移完成")
