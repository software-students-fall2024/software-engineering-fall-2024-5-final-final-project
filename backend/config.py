import os
from datetime import timedelta

class Config:
    # MongoDB配置
    MONGO_URI = 'mongodb://admin:password@mongodb:27017/bugcreator?authSource=admin'
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class TestConfig(Config):
    # 智能判断测试环境：CI环境使用localhost，Docker环境使用mongodb
    MONGODB_HOST = 'localhost' if os.getenv('CI') else 'mongodb'
    MONGO_URI = f"mongodb://{os.getenv('MONGO_ROOT_USERNAME')}:{os.getenv('MONGO_ROOT_PASSWORD')}@{MONGODB_HOST}:27017/test_blog?authSource=admin"
    TESTING = True
    JWT_SECRET_KEY = "test-secret-key"
