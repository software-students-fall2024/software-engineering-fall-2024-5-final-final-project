import bcrypt
from flask import jsonify

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def response(data=None, message=None, status=200):
    res = {}
    if data is not None:
        res['data'] = data
    if message is not None:
        res['message'] = message
    return jsonify(res), status
