from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key-here"

    # Configure session cookie settings
    app.config["SESSION_COOKIE_PATH"] = "/"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5000", "http://frontend:5000"],
    )

    login_manager.init_app(app)

    from backend.routes import routes

    app.register_blueprint(routes)

    return app
