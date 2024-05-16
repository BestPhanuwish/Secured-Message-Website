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

# engine2 = create_engine("sqlite:///database/main.db", echo=True)
# # initializes the database
# Base.metadata.create_all(engine2)


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


# The structure for User Permissions table
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     role = db.Column(db.String(20), default='student')  # Default role
