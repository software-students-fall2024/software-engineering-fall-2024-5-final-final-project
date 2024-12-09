from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import mongo
from app.models import User, Post, Comment
from app.utils import hash_password, check_password, response
from bson import ObjectId
import re
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # 验证必要字段
    if not all(k in data for k in ["username", "email", "password"]):
        return response(message="Missing required fields", status=400)

    # 验证邮箱格式
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, data["email"]):
        return response(message="Invalid email format", status=400)

    # 检查邮箱是否已存在
    if mongo.db.users.find_one({"email": data["email"]}):
        return response(message="Email already registered", status=400)

    # 创建新用户
    user = User(
        username=data["username"],
        email=data["email"],
        password=hash_password(data["password"]),
    )

    # 保存到数据库
    mongo.db.users.insert_one(user.to_dict())

    return response(
        data={"username": user.username, "email": user.email},
        message="User registered successfully",
        status=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    # 验证必要字段
    if not all(k in data for k in ["email", "password"]):
        return response(message="Missing required fields", status=400)

    # 查找用户
    user = mongo.db.users.find_one({"email": data["email"]})
    if not user or not check_password(data["password"], user["password"]):
        return response(message="Invalid email or password", status=401)

    # 创建访问令牌
    access_token = create_access_token(identity=str(user["_id"]))

    return response(
        data={
            "access_token": access_token,
            "user": {"username": user["username"], "email": user["email"]},
        },
        message="Login successful",
    )


post_bp = Blueprint("post", __name__)


@post_bp.route("/posts", methods=["POST"])
@jwt_required()
def create_post():
    try:
        data = request.get_json()

        if not data or "title" not in data or "content" not in data:
            return jsonify({"message": "Missing required fields"}), 400

        current_user_id = ObjectId(get_jwt_identity())

        post = Post(
            title=data["title"],
            content=data["content"],
            author_id=current_user_id,
            tags=data.get("tags", []),
        )

        result = mongo.db.posts.insert_one(post.to_dict())

        return jsonify({
            "message": "Post created successfully",
            "data": {"post_id": str(result.inserted_id)},
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@post_bp.route("/posts", methods=["GET"])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if page < 1 or per_page < 1:
        return jsonify({'message': 'Invalid pagination parameters'}), 400

    skip = (page - 1) * per_page

    posts = list(mongo.db.posts.find().skip(skip).limit(per_page))

    for post in posts:
        post["_id"] = str(post["_id"])
        post["author_id"] = str(post["author_id"])

    return jsonify({
        "data": posts,
        "page": page,
        "per_page": per_page,
        "total": mongo.db.posts.count_documents({}),
    }), 200


@post_bp.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    try:
        post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            return jsonify({"message": "Post not found"}), 404

        post["_id"] = str(post["_id"])
        post["author_id"] = str(post["author_id"])

        author = mongo.db.users.find_one({"_id": ObjectId(post["author_id"])})
        if author:
            post["author_username"] = author["username"]
        else:
            post["author_username"] = "Anonymous"

        return jsonify({"data": post}), 200
    except Exception as e:
        return jsonify({"message": "Invalid post ID"}), 400


@post_bp.route("/posts/<post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    try:
        current_user_id = ObjectId(get_jwt_identity())
        post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

        if not post:
            return jsonify({"message": "Post not found"}), 404

        if ObjectId(post["author_id"]) != current_user_id:
            return jsonify({"message": "Unauthorized"}), 403

        data = request.get_json()
        if not data.get("title") and not data.get("content"):
            return jsonify({"message": "Title or content cannot be empty"}), 400

        update_data = {
            "title": data.get("title", post["title"]),
            "content": data.get("content", post["content"]),
            "tags": data.get("tags", post["tags"]),
            "updated_at": datetime.utcnow(),
        }

        mongo.db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": update_data})

        return jsonify({"message": "Post updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@post_bp.route("/posts/<post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    try:
        current_user_id = ObjectId(get_jwt_identity())
        post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

        if not post:
            return jsonify({"message": "Post not found"}), 404

        if ObjectId(post["author_id"]) != current_user_id:
            return jsonify({"message": "Unauthorized"}), 403

        mongo.db.posts.delete_one({"_id": ObjectId(post_id)})

        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@post_bp.route("/posts/<post_id>", methods=["POST"])  
@jwt_required()
def create_comment(post_id):
    try:
        data = request.get_json()

        if not data or not data.get("content"):
            return jsonify({"message": "Comment content cannot be empty"}), 400

        current_user_id = ObjectId(get_jwt_identity())
        author = mongo.db.users.find_one({"_id": current_user_id})
        
        if not author:
            return jsonify({"message": "User not found"}), 404

        comment = Comment(
            content=data["content"],
            author_username=author["username"],
        )

        result = mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment.to_dict()}}
        )

        if result.modified_count == 0:
            return jsonify({"message": "Post not found"}), 404

        return jsonify({"message": "Comment created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@post_bp.route("/posts/my-posts", methods=["GET"])
@jwt_required()
def get_user_posts():
    try:
        current_user_id = ObjectId(get_jwt_identity())
        posts = list(mongo.db.posts.find({"author_id": str(current_user_id)}))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["author_id"] = str(post["author_id"])

        return jsonify({"data": posts}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
