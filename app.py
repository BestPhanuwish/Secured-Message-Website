'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
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

# function to verify
def verify_user(username, password):
    conn = sqlite3.connect('database/main.db')
    c = conn.cursor()
    
    result = c.fetchone()
    if result:
        hashed_password = result[0]
        # Verify the password by hashing it with the stored salt and comparing it with the stored hash
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print("Authentication successful")
        else:
            print("Authentication failed")
            return "Authentication failed"
    else:
        print("User not found")
        return "User not found"

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    now_password = request.json.get("password")

    verify_user(username, now_password)

    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# function to encrypt
def Encryption_user(username, password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")

    new_pwd = Encryption_user(username, password)

    if db.get_user(username) is None:
        db.insert_user(username, new_pwd)
        return url_for('home', username=username)
    return "Error: User already exists!"

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
