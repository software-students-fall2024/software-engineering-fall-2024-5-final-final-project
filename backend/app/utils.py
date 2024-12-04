import bcrypt
from flask import jsonify

def hash_password(password):
    if not password:
        raise ValueError("Password cannot be empty")
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    if not password or not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except (TypeError, ValueError):
        return False

def response(data=None, message=None, status=200):
    """
    统一的响应格式
    :param data: 响应数据
    :param message: 响应消息
    :param status: HTTP状态码
    :return: JSON响应
    """
    res = {}
    if data is not None:
        res['data'] = data
    if message is not None:
        res['message'] = message
    return jsonify(res), status

def handle_error(error):
    """
    统一的错误处理
    :param error: 错误对象
    :return: JSON响应
    """
    if isinstance(error, ValueError):
        return response(message=str(error), status=400)
    return response(message="Internal server error", status=500)
