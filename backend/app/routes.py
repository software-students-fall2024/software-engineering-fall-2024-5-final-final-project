from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import mongo
from app.models import User
from app.utils import hash_password, check_password, response
from bson import ObjectId
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # 验证必要字段
    if not all(k in data for k in ['username', 'email', 'password']):
        return response(message="Missing required fields", status=400)

    # 验证邮箱格式
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, data['email']):
        return response(message="Invalid email format", status=400)

    # 检查邮箱是否已存在
    if mongo.db.users.find_one({'email': data['email']}):
        return response(message="Email already registered", status=400)

    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        password=hash_password(data['password'])
    )

    # 保存到数据库
    mongo.db.users.insert_one(user.to_dict())

    return response(
        data={"username": user.username, "email": user.email},
        message="User registered successfully",
        status=201
    )

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # 验证必要字段
    if not all(k in data for k in ['email', 'password']):
        return response(message="Missing required fields", status=400)

    # 查找用户
    user = mongo.db.users.find_one({'email': data['email']})
    if not user or not check_password(data['password'], user['password']):
        return response(message="Invalid email or password", status=401)

    # 创建访问令牌
    access_token = create_access_token(identity=str(user['_id']))

    return response(
        data={
            "access_token": access_token,
            "user": {
                "username": user['username'],
                "email": user['email']
            }
        },
        message="Login successful"
    )
