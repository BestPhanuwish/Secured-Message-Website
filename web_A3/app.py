import secrets
from flask import Flask, url_for, render_template, flash, request, redirect
import sqlite3
import sqlalchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()

# 创建一个函数用来获取数据库链接
def get_db_connection():
    # 创建数据库链接到database.db文件
    conn = sqlite3.connect('database.db')
    # 设置数据的解析方法，有了这个设置，就可以像字典一样访问每一列数据
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('select * from posts where id = ?', (post_id,)).fetchone()
    return post

@app.route('/')
def index():
    # 调用上面的函数，获取链接
    conn = get_db_connection()
    # 查询所有数据，放到变量posts中
    posts = conn.execute('SELECT * FROM posts order by created desc').fetchall()
    conn.close()
    #把查询出来的posts传给网页
    return render_template('index.html', posts=posts)

@app.route('/posts/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/posts/new', methods=('GET', 'POST'))
def new():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash("标题不能为空", category='error')
        elif not content:
            flash("内容不能为kong", 'info')
        else:
            conn = get_db_connection()
            conn.execute('insert into posts (title, content) values(?, ?)', (title, content))
            conn.commit()
            conn.close()
            flash("保存成功", 'success')
            return redirect(url_for('index'))

    return render_template('new.html')

@app.route('/posts/<int:post_id>/edit', methods=('GET', 'POST'))
def edit(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('title can not be empty')
        else:
            conn = get_db_connection()
            conn.execute('Update posts SET title = ?, content = ?'
                         'Where id = ?',
                         (title, content, post_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=('POST',))
def delete(post_id):
    post = get_post(post_id)
    conn = get_db_connection()
    conn.execute('DELEte from posts where id =?', (post_id, ))
    conn.commit()
    conn.close()
    flash( '删除成功!'.format(post['title']) )
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    # 模拟从数据库中搜索文章
    articles = search_articles(keyword)  # 假设这个函数根据关键词返回文章列表
    print(articles)
    return render_template('search_results.html', articles=articles)

def search_articles(keyword):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('database.db')
    # 创建一个游标对象
    cursor = conn.cursor()

    # 构建查询语句，使用通配符实现模糊匹配
    search_pattern = f'%{keyword}%'
    query = "SELECT id, title FROM posts WHERE title LIKE ? OR content LIKE ?"

    # 执行查询
    cursor.execute(query, (search_pattern, search_pattern))

    # 获取所有匹配的记录
    results = cursor.fetchall()

    # 关闭游标和连接
    cursor.close()
    conn.close()

    # 返回结果
    return results


# # Account Permission Part
# from flask import session
# from functools import wraps
# from web_A3 import db
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#
# # Login required decorator
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'logged_in' not in session:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function
#
# # Role required decorator
# def role_required(role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if 'role' not in session or session['role'] != role:
#                 return redirect(url_for('login', next=request.url))
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         user = User.query.filter_by(username=username).first()
#         if user:
#             session['logged_in'] = True
#             session['username'] = user.username
#             session['role'] = user.role
#             return redirect(url_for('index'))
#         return 'User not found'
#     return render_template('login.html')
#
# @app.route('/discussion')
# @login_required
# @role_required('student')
# def discussion():
#     return 'Discussion Board for Students'
#
# @app.route('/moderate')
# @login_required
# @role_required('instructor')
# def moderate():
#     return 'Discussion Moderation Panel for Instructors'


if __name__ == '__main__':
    app.run(debug=True, port=5010)

