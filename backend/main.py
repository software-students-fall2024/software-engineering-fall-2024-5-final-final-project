from flask import Flask
from flask_cors import CORS
from routes import routes
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    CORS(app,
         supports_credentials=True,
         origins=['http://localhost:5000', 'http://frontend:5000'],
         allow_headers=['Content-Type'],
         expose_headers=['Set-Cookie'])
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.register_blueprint(routes)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001)