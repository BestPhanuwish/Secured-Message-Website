'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''
from datetime import timedelta

import eventlet
from flask import Flask, render_template, request, abort, url_for, flash
from flask_socketio import SocketIO
from flask import redirect
import db
import secrets
import bcrypt
import sqlite3
from cryptography.fernet import Fernet
from flask import Flask, request, session, jsonify
from functools import wraps

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

message_history_db = {}


# index page
@app.route("/")
def index():
    return render_template("index.jinja")


# login page
@app.route("/login")
def login():
    return render_template("login.jinja")


# friend page
@app.route("/friend")
def friend():
    return render_template("friend.jinja")


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")


# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)

    username_enter = request.json.get("username")
    password_enter = request.json.get("password")

    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    enc_password = bcrypt.hashpw(password_enter.encode('utf-8'), salt)

    if db.get_user(username_enter) is None:
        db.insert_user(username_enter, enc_password)
        print("Now, waiting for following page")
        return url_for('login', username=username_enter)

    return "Error: User already exists!"


# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    Username_ENter = request.json.get("username")
    User_Enter_Pwd = request.json.get("password")

    # Connect to the SQLite database
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user WHERE username = ?", (Username_ENter,))
    result = cursor.fetchone()

    if result:
        # print("result: ", result)
        hashed_password = result[1]
        
        salt = hashed_password[:29]  # 29 is the length of the salt in bcrypt
        pwd_hashed = hashed_password[29:]

        hashed_user_input_password = bcrypt.hashpw(User_Enter_Pwd.encode('utf-8'), salt)

        if hashed_password != hashed_user_input_password:
            # print("hash_password: ", hashed_password)
            # print("UserEnter_Pwd: ", hashed_user_input_password)
            return "Error Password not match"

        else:
            session['username'] = Username_ENter
            print("Welcome to join chat room")
            return url_for('home', username=request.json.get("username"))
    else:
        return "Error username not found"


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404


# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)

    certify_username = session.get('username')
    if certify_username is None:
        print("This user not login")
        return redirect(url_for('login'))

    return render_template("home.jinja", username=request.args.get("username"))


# New function for A3
#
# app.permanent_session_lifetime = timedelta(days=365)
#
# essays = {}  # This will store essays with id as key
# views_count = {}  # This will store views count for each essay
#
# @app.route('/')
# def index():
#     return render_template('show.html', essays=essays)
#
# @app.route('/submit', methods=['GET', 'POST'])
# def submit_essay():
#     if request.method == 'POST':
#         title = request.form['title']
#         content = request.form['content']
#         author = session.get('username')
#         essay_id = len(essays) + 1
#         essays[essay_id] = {'title': title, 'content': content, 'author': author}
#         views_count[essay_id] = 0
#         return redirect(url_for('index'))
#     return render_template('submit_essay.html')
#
# @app.route('/essay/<int:essay_id>')
# def view_essay(essay_id):
#     views_count[essay_id] += 1
#     return render_template('view_essay.html', essay=essays[essay_id], view_count=views_count[essay_id])
#
# @app.route('/delete/<int:essay_id>')
# def delete_essay(essay_id):
#     if session.get('username') == essays[essay_id]['author']:
#         del essays[essay_id]
#         del views_count[essay_id]
#     return redirect(url_for('index'))


# 创建一个函数用来获取数据库链接
def get_db_connection():
    # 创建数据库链接到database.db文件
    conn = sqlite3.connect('web_A3/database.db')
    # 设置数据的解析方法，有了这个设置，就可以像字典一样访问每一列数据
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('select * from posts where id = ?', (post_id,)).fetchone()
    return post

@app.route('/web_index')
def web_index():
    # 调用上面的函数，获取链接
    conn = get_db_connection()
    # 查询所有数据，放到变量posts中
    posts = conn.execute('SELECT * FROM posts order by created desc').fetchall()
    conn.close()
    #把查询出来的posts传给网页
    return render_template('show.html', posts=posts)

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
            flash("The title can not be empty", category='error')
        elif not content:
            flash("内容不能为kong", 'info')
        else:
            conn = get_db_connection()
            conn.execute('insert into posts (title, content) values(?, ?)', (title, content))
            conn.commit()
            conn.close()
            flash("save successfully", 'success')
            return redirect(url_for('web_index'))

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
            return redirect(url_for('web_index'))

    return render_template('edit.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=('POST',))
def delete(post_id):
    post = get_post(post_id)
    conn = get_db_connection()
    conn.execute('DELEte from posts where id =?', (post_id, ))
    conn.commit()
    conn.close()
    flash('delete successful!'.format(post['title']))
    return redirect(url_for('web_index'))

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
    conn = sqlite3.connect('web_A3/database.db')
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

@app.route('/try_comment')
def try_comment():
    return render_template('try_comment.html')



if __name__ == '__main__':
    ssl_args = {
        'certfile': './database/new_localhost.crt',
        'keyfile': './database/new_localhost.key'
    }

    listener = eventlet.listen(('localhost', 5000))

    ssl_listener = eventlet.wrap_ssl(listener, **ssl_args, servere_side=True)

    eventlet.wsgi.server(ssl_listener, app)
