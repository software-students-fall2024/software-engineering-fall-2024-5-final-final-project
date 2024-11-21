from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

load_dotenv()

def create_app():
    
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'defaultsecretkey')

    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)
    
    #Login manager
    manager = LoginManager()
    manager.init_app(app)
    manager.login_view = 'login'

    #Get user info using mongo
    users=db.UserData.find()
    userList=list(users)

    #User class
    class User(UserMixin):
        def __init__(self, user_data):
            self.id = str(user_data['_id'])
            self.username = user_data['username']

        @staticmethod
        def get(user_id):
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        pass

    @manager.user_loader
    def user_loader(user_id):
        return User.get(user_id)

    @manager.request_loader
    def request_loader(request):
        username = request.form.get('username')

        if username:
            user_data = db.users.find_one({'username': username})

            if user_data:
                user = User(user_data)
                password = request.form.get('password')

                if check_password_hash(user_data['password'], password):
                    return user
        return None
    
    #Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user_data = db.users.find_one({'username': username})

            if user_data and check_password_hash(user_data['password'], password):
                user = User(user_data)
                login_user(user)
                flash('Log in success!')
                return redirect(url_for('home'))
            
            flash('Invalid username or password')

        return render_template('login.html')
    
    #Create account route
    @app.route('/createAccount', methods=['GET', 'POST'])
    def createAccount():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            existing_user = db.users.find_one({'username': username})

            if existing_user is None:
                hashed_password = generate_password_hash(password)

                db.users.insert_one({
                    'username': username,
                    'password': hashed_password
                })

                flash('Account created! Please log in.')
                return redirect(url_for('login'))
            
            flash('Username already exists. Please choose a different username.')

        return render_template('createAccount.html')
    
    #Log out route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.')
        return redirect(url_for('home'))
    
    @app.route("/")
    @login_required
    def home():
        """
        Route for the home page
        """
        return render_template("index.html")

    return app

if __name__ =="__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", 5001)
    app = create_app()
    app.run(port=FLASK_PORT)