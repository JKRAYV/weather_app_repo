from mongodbsetup import user
from flask import json
from bson import json_util
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

def parse_json(data):
    return json.loads(json_util.dumps(data))

# authenticate user
def authenticate_login(credentials):
    username = credentials['username']
    password = credentials['password']

    user_in_db = user.find_one({'username': username}) # search for user in database
    if user_in_db and check_password_hash(user_in_db['password'], password):
        access_token = create_access_token(identity=parse_json(user_in_db))
        return {
            "message": "Login success!",
            "username": user_in_db['username'],
            "access_token": access_token
            }, 200
    else:
        return {"message": "Invalid credentials"}, 401

#create user
def create_user(userObject):
    hashed_password = generate_password_hash(userObject['password'], method='sha256')
    return user.insert_one({
        "first_name" : userObject["first_name"],
        "last_name" : userObject["last_name"],
        "username" : userObject["username"],
        "email" : userObject["email"],
        "address" : userObject["address"],
        "password" : hashed_password
    })

#update user
def update_user_by_id(id, userObject):
    # Defining the filter
    filter = {"_id": id}
    # defining what we want updated
    hashed_password = generate_password_hash(userObject['password'], method='sha256')
    update = {"$set": {
        "first_name" : userObject["first_name"],
        "last_name" : userObject["last_name"],
        "username" : userObject["username"],
        "email" : userObject["email"],
        "address" : userObject["address"],
        "password" : hashed_password
    }}
    return user.update_one(filter, update)

def update_user_by_username(username, userObject):
    hashed_password = generate_password_hash(userObject['password'], method='sha256')
    # Defining the filter
    filter = {"username": username}
    # defining what we want updated
    update = {"$set": {
        "first_name" : userObject["first_name"],
        "last_name" : userObject["last_name"],
        "username" : userObject["username"],
        "email" : userObject["email"],
        "address" : userObject["address"],
        "password" : hashed_password
    }}
    return user.update_one(filter, update)

# find
def find_all():
    return parse_json(user.find({}))

def find_by_username(username):
    return parse_json(user.find_one({"username": username}))

def find_by_full_name(name):
    first_name, last_name = name.split()
    return parse_json(user.find({"first_name": first_name,
                      "last_name": last_name}))

def find_by_first_name(name):
    return parse_json(user.find({"first_name": name}))

def find_by_last_name(name):
    return parse_json(user.find({"last_name": name}))

def find_by_id(id):
    return parse_json(user.find_one({"_id":id}))

#delete
def delete_user_by_id(id):
    return user.delete_one({"_id":id})

def delete_user_by_username(username):
    return user.delete_one({"username": username})