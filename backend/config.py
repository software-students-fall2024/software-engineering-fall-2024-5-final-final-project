import os
from datetime import timedelta

class Config:
    # MongoDB配置
    MONGO_URI = f"mongodb://{os.getenv('MONGO_ROOT_USERNAME')}:{os.getenv('MONGO_ROOT_PASSWORD')}@mongodb:27017/{os.getenv('MONGO_DATABASE')}?authSource=admin"
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class TestConfig(Config):
    # 测试数据库配置
    MONGO_URI = f"mongodb://{os.getenv('MONGO_ROOT_USERNAME')}:{os.getenv('MONGO_ROOT_PASSWORD')}@localhost:27017/test_db?authSource=admin"
    TESTING = True
