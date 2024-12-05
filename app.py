from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId


load_dotenv()

def create_app(test_config=None):
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_temporary_secret_key')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    app.config['MONGO_DBNAME'] = os.getenv('MONGO_DBNAME', 'test_db')

    try:
        cxn = pymongo.MongoClient(app.config["MONGO_URI"])
        db = cxn[app.config["MONGO_DBNAME"]]
        cxn.admin.command("ping")
        print("MongoDB connection successful.")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        raise
    
    manager = LoginManager()
    manager.init_app(app)
    manager.login_view = 'createAccount'

    users=db.UserData.find()
    userList=list(users)

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
            
            flash('Invalid username or password', 'error')

        return render_template('login.html')
    
    #Create account route
    @app.route('/createAccount', methods=['GET', 'POST'])
    def createAccount():
        if request.method == 'POST':
            first_name = request.form['first-name']
            last_name = request.form['last-name']
            username = request.form['username']
            password = request.form['password']
            existing_user = db.users.find_one({'username': username})

            if existing_user is None:
                hashed_password = generate_password_hash(password)

                db.users.insert_one({
                    'first-name': first_name,
                    'last-name': last_name,
                    'username': username,
                    'password': hashed_password
                })

                flash('Account created! Please log in.')
                return redirect(url_for('login'))
            
            flash('Username already exists. Please choose a different username.')

        return render_template('createAccount.html')
    
    #Log out route
    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.')
        return redirect(url_for('login'))
    
    @app.route("/")
    @login_required
    def home():
        """
        Route for the home page
        """
        wishes = db.wishes.find({"user_id": current_user.id}).sort("created_at", -1)
        return render_template("index.html", wishes=wishes)
    
    @app.route("/wishlist/<username>")
    def wishlist(username):
        #view specific users wishlist
        user = db.users.find_one({"username": username})
        if not user:
            flash("user not found")
            return redirect(url_for("home"))
        
        wishes = db.wishes.find({"user_id": str(user["_id"])}).sort("created_at", -1)
        return render_template("wishlist.html", wishes=wishes, user=user)

    
    @app.route("/add",methods=["GET","POST"])
    @login_required
    def add():
        itemImage=request.form.get("item_image")
        itemName=request.form.get("item_name")
        itemPrice=request.form.get("item_price")
        itemLink=request.form.get("item_link")
        comments=request.form.get("item_comments")
        
        if itemName and itemPrice and itemLink: #validate
            db.wishes.insert_one({ #insert into db
                "image": itemImage,
                "name":itemName,
                "price":itemPrice,
                "link":itemLink,
                "comments":comments,
                "user_id":current_user.id
            })
            flash("Item added!")
            return redirect(url_for("home"))
        else:
            flash("Missing information")
        return render_template("add.html")
    
    #Edit route
    @app.route("/edit/<wish_id>", methods=["GET", "POST"])
    @login_required
    def edit(wish_id):
    #get the gift id
        wish = db.wishes.find_one({"_id": ObjectId(wish_id), "user_id": current_user.id})
        if not wish:
            flash("Wish not found or you are not authorized to edit it.")
            return redirect(url_for('home'))

        if request.method == "POST":
            itemImage = request.form.get("item_image")
            itemName = request.form.get("item_name")
            itemPrice = request.form.get("item_price")
            itemLink = request.form.get("item_link")
            itemComments = request.form.get("item_comments")

            #valid input and update
            if itemName and itemPrice:
                db.wishes.update_one(
                    {"_id": ObjectId(wish_id)},
                    {"$set": {
                        "image": itemImage,
                        "name": itemName,
                        "price": itemPrice,
                        "link": itemLink,
                        "comments": itemComments
                    }}
                )
                flash("Wish updated successfully!")
                return redirect(url_for("home"))
            else:
                flash("Missing required information.")
    
        # Render the edit page with the wish details pre-filled
        return render_template("edit.html", wish=wish)
    
    #Delete Route
    @app.route("/delete/<wish_id>", methods=["POST"])
    @login_required
    def delete(wish_id):
        # Find and delete the wish if it belongs to the current user
        result = db.wishes.delete_one({"_id": ObjectId(wish_id), "user_id": current_user.id})
        if result.deleted_count == 0:
            flash("Wish not found or you are not authorized to delete it.")
        else:
            flash("Wish deleted successfully!")
        return redirect(url_for('home'))

    
    return app

if __name__ =="__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", 5001)
    app = create_app()
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=True)