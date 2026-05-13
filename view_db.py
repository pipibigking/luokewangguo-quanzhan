import sqlite3

def show_database(db_path, db_name):
    output_lines = []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    output_lines.append('\n' + '=' * 70)
    output_lines.append('数据库: ' + db_name)
    output_lines.append('路径: ' + db_path)
    output_lines.append('=' * 70)
    
    if not tables:
        output_lines.append('[状态]: 空数据库（无表）')
        conn.close()
        return output_lines
    
    output_lines.append('[表数量]: ' + str(len(tables)))
    output_lines.append('[表列表]: ' + ', '.join(tables))
    
    for table_name in tables:
        output_lines.append('\n  ┌' + '-' * 68 + '┐')
        output_lines.append('  │ 表: ' + table_name)
        output_lines.append('  ├' + '-' * 68 + '┤')
        
        cursor.execute("PRAGMA table_info(" + table_name + ")")
        columns = cursor.fetchall()
        
        output_lines.append('  │ [字段结构]:')
        col_line = '  │   '
        for col in columns:
            col_line += col[1] + ' (' + col[2] + ') | '
        output_lines.append(col_line)
        
        cursor.execute("SELECT * FROM " + table_name + " LIMIT 3")
        rows = cursor.fetchall()
        
        output_lines.append('  │ [数据预览] (最多3行):')
        if len(rows) == 0:
            output_lines.append('  │   (空表)')
        else:
            for row in rows:
                row_str = '  │   ' + str(row)
                if len(row_str) > 80:
                    row_str = row_str[:80] + '...'
                output_lines.append(row_str)
            
            cursor.execute("SELECT COUNT(*) FROM " + table_name)
            count = cursor.fetchone()[0]
            output_lines.append('  │   ... 共 ' + str(count) + ' 行')
        
        output_lines.append('  └' + '-' * 68 + '┘')
    
    conn.close()
    return output_lines

def main():
    output_lines = []
    output_lines.append('=' * 70)
    output_lines.append('数据库结构与数据展示')
    output_lines.append('=' * 70)
    
    # 检查各个数据库文件
    db_files = [
        ('locke_pets.db', '项目根目录 - locke_pets.db'),
        ('system_data.db', '项目根目录 - system_data.db'),
        ('backend/locke_pets.db', '后端目录 - locke_pets.db')
    ]
    
    for db_path, db_name in db_files:
        output_lines.extend(show_database(db_path, db_name))
    
    # 添加说明
    output_lines.append('\n' + '=' * 70)
    output_lines.append('📝 数据存储说明')
    output_lines.append('=' * 70)
    output_lines.append('后端 main.py 配置的数据库路径:')
    output_lines.append('  DATABASE_URL = sqlite:///backend/locke_pets.db')
    output_lines.append('')
    output_lines.append('当前状态:')
    output_lines.append('  - backend/locke_pets.db: 空数据库')
    output_lines.append('  - system_data.db: 包含实际数据')
    output_lines.append('')
    output_lines.append('⚠️ 重要: 网页中修改/添加的数据会存储到 backend/locke_pets.db')
    output_lines.append('         当前这个文件是空的，需要先初始化或复制数据！')
    
    with open('database_structure.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print('数据库报告已生成: database_structure.txt')

if __name__ == '__main__':
    main()