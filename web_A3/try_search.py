import sqlite3

def search_articles(keyword):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('database.db')
    # 创建一个游标对象
    cursor = conn.cursor()

    # 构建查询语句，使用通配符实现模糊匹配
    search_pattern = f'%{keyword}%'
    query = "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?"

    # 执行查询
    cursor.execute(query, (search_pattern, search_pattern))

    # 获取所有匹配的记录
    results = cursor.fetchall()

    # 关闭游标和连接
    cursor.close()
    conn.close()

    # 返回结果
    return results

# 示例用法
keyword = "hello"
articles = search_articles(keyword)
for article in articles:
    print(article[0])  # 每个 article 是一个包含 id, title, 和 content 的元组
