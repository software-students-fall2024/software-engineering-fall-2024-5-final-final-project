from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from config import Config

mongo = PyMongo()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # 加载配置
    if isinstance(config_class, str):
        app.config.from_object(config_class)
    else:
        app.config.from_object(config_class)
    
    # 初始化扩展
    mongo.init_app(app)
    jwt.init_app(app)
    
    # 注册蓝图
    from app.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app
