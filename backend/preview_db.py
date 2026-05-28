import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'system_data.db')

def get_table_counts():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    results = {}
    for table in tables:
        cursor.execute("SELECT COUNT(*) FROM %s" % table)
        count = cursor.fetchone()[0]
        results[table] = count
    
    conn.close()
    return results

def get_pets_summary():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT "group", COUNT(*), MIN(price), MAX(price), AVG(price) FROM pets GROUP BY "group"')
    groups = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM pets WHERE is_active = 1")
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT attributes) FROM pets")
    attr_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "groups": groups,
        "active_count": active_count,
        "attr_count": attr_count
    }

def get_admin_accounts():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, created_at FROM admin_accounts ORDER BY created_at")
    accounts = cursor.fetchall()
    
    conn.close()
    return accounts

def get_announcement():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT content, updated_at FROM announcement LIMIT 1")
    result = cursor.fetchone()
    
    conn.close()
    return result

def get_messages_summary():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM messages")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages WHERE is_read = 0")
    unread = cursor.fetchone()[0]
    
    cursor.execute("SELECT nickname, content, created_at FROM messages ORDER BY created_at DESC LIMIT 3")
    recent = cursor.fetchall()
    
    conn.close()
    return {
        "total": total,
        "unread": unread,
        "recent": recent
    }

def get_site_config():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT key, value FROM site_config WHERE key IN ('site_title', 'site_subtitle', 'version', 'author_name')")
    configs = cursor.fetchall()
    
    conn.close()
    return configs

def main():
    print("=" * 60)
    print("          洛克王国异色精灵数据库预览")
    print("=" * 60)
    
    print("\n【表数据统计】")
    print("-" * 40)
    table_counts = get_table_counts()
    for table, count in sorted(table_counts.items()):
        print("  %s: %d 条记录" % (table, count))
    
    print("\n【精灵数据摘要】")
    print("-" * 40)
    pets_info = get_pets_summary()
    print("  活跃精灵数: %d" % pets_info['active_count'])
    print("  属性种类数: %d" % pets_info['attr_count'])
    print("\n  分组统计:")
    for group, count, min_price, max_price, avg_price in pets_info['groups']:
        print("    %s: %d只 | 价格范围: %d-%d (平均%d)" % (group, count, min_price, max_price, int(avg_price)))
    
    print("\n【管理员账号】")
    print("-" * 40)
    accounts = get_admin_accounts()
    if accounts:
        for username, created_at in accounts:
            print("  - %s" % username)
    else:
        print("  暂无管理员账号")
    
    print("\n【系统公告】")
    print("-" * 40)
    announcement = get_announcement()
    if announcement:
        content = announcement[0][:80] + "..." if len(announcement[0]) > 80 else announcement[0]
        print("  %s" % content)
    else:
        print("  暂无公告")
    
    print("\n【留言统计】")
    print("-" * 40)
    messages = get_messages_summary()
    print("  总留言数: %d" % messages['total'])
    print("  未读留言: %d" % messages['unread'])
    if messages['recent']:
        print("\n  最新3条留言:")
        for nickname, content, created_at in messages['recent']:
            content = content[:30] + "..." if len(content) > 30 else content
            print("    %s: %s" % (nickname, content))
    
    print("\n【站点配置】")
    print("-" * 40)
    configs = get_site_config()
    for key, value in configs:
        print("  %s: %s" % (key, value))
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
