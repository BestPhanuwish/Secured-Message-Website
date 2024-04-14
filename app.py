'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
from flask import redirect
import db
import secrets
import bcrypt
import sqlite3

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

    username = request.json.get("username")
    password = request.json.get("password")

    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    enc_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    if db.get_user(username) is None:
        db.insert_user(username, enc_password)
        return url_for('home', username=username)
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
        hashed_password = result[1]

        if hashed_password == User_Enter_Pwd:
            return "Error Password not match"
        else:
            return url_for('home', username=request.json.get("username"))


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    return render_template("home.jinja", username=request.args.get("username"))


if __name__ == '__main__':
    socketio.run(app)
