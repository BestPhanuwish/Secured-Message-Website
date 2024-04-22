'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=True)

# initializes the database
Base.metadata.create_all(engine)


# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine2 = create_engine("sqlite:///database/chat_database.db", echo=True)
# initializes the database
Base.metadata.create_all(engine2)


# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.query(User).filter_by(username=username).first()

### Below is what I've implemented ###

# add friend to the database
def add_friend(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.add_friend(friend_username)
        session.commit()

# add friend sent to the database
def add_friend_sent(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.add_friend_sent(friend_username)
        session.commit()

# remove friend sent on the database
def remove_friend_sent(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.remove_friend_sent(friend_username)
        session.commit()

# add friend request to the database
def add_friend_request(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.add_friend_request(friend_username)
        session.commit()
        
# remove friend request on the database
def remove_friend_request(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.remove_friend_request(friend_username)
        session.commit()
