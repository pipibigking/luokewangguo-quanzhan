import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locke_pets.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE pets ADD COLUMN is_active BOOLEAN DEFAULT 1')
    print('added is_active column')
except sqlite3.OperationalError as e:
    if 'duplicate column' in str(e).lower():
        print('is_active column already exists')
    else:
        print(f'error adding column: {e}')

cursor.execute('CREATE TABLE IF NOT EXISTS announcement (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT DEFAULT "", updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)')
cursor.execute('SELECT COUNT(*) FROM announcement')
count = cursor.fetchone()[0]
if count == 0:
    cursor.execute('INSERT INTO announcement (content) VALUES (?)', ('欢迎来到笑笑屁屁-洛克王国异色精灵交易平台！新精灵即将上架，敬请期待~',))
    print('inserted default announcement')
else:
    print('announcement table already has data')

conn.commit()
conn.close()
print('migration complete')
