'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request
import sqlite3

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

### Old code that I don't want to touch ###

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))


# send message event handler
@socketio.on("send")
def send(username, message, room_id):
    emit("incoming", (f"{username}: {message}"), to=room_id)
    print("room_id: ", room_id)
    print("message: ", message)
    print("username: ", username)
    database = sqlite3.connect("database/chat_database.db")
    cursor = database.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS history (room_id, sender, messages)")

    cursor.execute("INSERT INTO history VALUES (?, ?, ?)", (room_id, username, message))
    database.commit()

    cursor.execute("SELECT * FROM history WHERE sender = ?", (username,))
    message_history = cursor.fetchall()
    for row in message_history:
        print("result:", row)
    
# join room event handler
# sent when the user joins a room
@socketio.on("get_receiver")    
def get_receiver(sender_name, receiver_name):
    print(sender_name)
    print(receiver_name)
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    # if the user is already inside of a room 
    if room_id is not None:
        
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

### New code that's implemented by me ###

# edge checking if sender and receiver are legit
def edge_sender_receiver_check(sender_name, receiver_name):
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown friend name!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"
    
    if receiver_name == sender_name:
        return "Go touch grass and find a friend!"
    
    if receiver_name in db.get_user(sender_name).friends:
        return f"You already had {receiver_name} as a friend!"
    
    if receiver_name in db.get_user(sender_name).friend_sent:
        return f"You already sent {receiver_name} a friend request!"
    
    if receiver_name in db.get_user(sender_name).friend_request:
        return f"Just accept a friend request from {receiver_name} already!"

# send request event handler
@socketio.on("send_request")
def send_request(sender_name, receiver_name):
    # make suer that sender and receiver name are legit
    error_message = edge_sender_receiver_check(sender_name, receiver_name)
    if error_message != None:
        return error_message
    
    # add the information to the database
    db.add_friend_sent(sender_name, receiver_name)
    db.add_friend_request(receiver_name, sender_name)
    
    return 0 # if success return number value

# accept friend request event handler
@socketio.on("accept_request")
def accept_request(user_name, requestor_name):
    receiver = db.get_user(requestor_name)
    if receiver is None:
        return "Unknown friend name!"
    
    sender = db.get_user(user_name)
    if sender is None:
        return "Unknown sender!"
    
    # modify information on the database
    db.add_friend(user_name, requestor_name)
    db.add_friend(requestor_name, user_name)
    db.remove_friend_request(user_name, requestor_name)
    db.remove_friend_sent(requestor_name, user_name)
    
    return 0

# decline friend request event handler
@socketio.on("decline_request")
def decline_request(user_name, requestor_name):
    receiver = db.get_user(requestor_name)
    if receiver is None:
        return "Unknown friend name!"
    
    sender = db.get_user(user_name)
    if sender is None:
        return "Unknown sender!"
    
    # modify information on the database
    db.remove_friend_request(user_name, requestor_name)
    db.remove_friend_sent(requestor_name, user_name)
    
    return 0

# boardcast event to reload friend section for every user that connected to this pipe
@socketio.on("reload_friend_section")
def reload_friend_section(sender_name, receiver_name):
    emit("reload", (sender_name, receiver_name), broadcast=True)

# get all the friend information from database and pass to client
@socketio.on("get_friend_info")
def get_friend_info(username):
    user = db.get_user(username)
    if user is None:
        return "Unknown user!"
    
    return {
        "friends": user.friends,
        "friend_sent": user.friend_sent,
        "friend_request": user.friend_request,
    }
    
