from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId  # To handle MongoDB ObjectIds
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random secret key

uri = "mongodb+srv://hugobray01:AmosBloomberg@splitsmart.ursnd.mongodb.net/?retryWrites=true&w=majority&appName=SplitSmart"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

mydb = client["SplitSmart"]
col_users = mydb["USERS"]
col_groups = mydb["GROUPS"]

#logged_in = False  # Tracks the user's logged-in state
#username = None  # Tracks the logged-in user's name


@app.route('/')
def base():
    return render_template("welcome.html")


@app.route("/main")
def home():
    if 'username' not in session:
        flash("Not logged in.  Please log in first")
        return redirect(url_for("login"))
    return render_template('home.html', username=session['username'])


@app.route('/groups')
def groups():
    if 'username' not in session:
        flash("Not logged in.  Please log in first")
        return redirect(url_for("login"))
        
    username = session['username']
    user = col_users.find_one({"name": username})
    user_groups = user.get("groups", [])
    
    # Fetch all group details
    group_details = []
    for group_id in user_groups:
        group = col_groups.find_one({"_id": group_id})
        if group:
            group["member_names"] = [member["name"] for member in group.get("group_members", [])]  # Fetch member names
            group_details.append(group)

    return render_template('groups.html', groups=group_details)



@app.route('/create-group', methods=["GET", "POST"])
def create_group():
    if 'username' not in session:
        flash("Not logged in.  Please log in first")
        return redirect(url_for("login"))

    if request.method == "POST":
        group_name = request.form.get("group_name")
        members = request.form.get("members").split(",")  # Split usernames by commas

        # Fetch user IDs for members
        member_objects = []
        for member_name in members:
            user = col_users.find_one({"name": member_name.strip()})
            if user:
                member_objects.append({"user_id": user["_id"], "name": user["name"]})
            else:
                flash(f"User '{member_name.strip()}' does not exist.", "error")
                return redirect(url_for("create_group"))

        # Create the group
        new_group = {
            "_id": str(ObjectId()),  # Generate a unique ID for the group
            "group_name": group_name,
            "group_members": member_objects,
            "expenses": []
        }

        col_groups.insert_one(new_group)

        # Add the group ID to each member's group list
        for member in member_objects:
            col_users.update_one(
                {"_id": member["user_id"]},
                {"$push": {"groups": new_group["_id"]}}
            )

        flash(f"Group '{group_name}' created successfully!", "success")
        return redirect(url_for("groups"))

    return render_template("create-groups.html")

@app.route('/add-expense', methods=["GET", "POST"])
def add_expense():
    if 'username' not in session:
        flash("Not logged in.  Please log in first")
        return redirect(url_for("login"))
        
        
    username = session['username']
    user = col_users.find_one({"name": username})
    if request.method == "POST":
        group_id = request.form.get("group_id")
        description = request.form.get("description")
        amount = float(request.form.get("amount"))
        paid_by = request.form.get("paid_by")
        split_among = request.form.get("split_among")
        split_among = eval(split_among)

        expense = {
            "expense_id": f"expense{len(col_groups.find_one({'_id': ObjectId(group_id)})['expenses']) + 1}",
            "description": description,
            "amount": amount,
            "paid_by": ObjectId(paid_by),
            "split_among": {ObjectId(k): v for k, v in split_among.items()},
            "timestamp": datetime.utcnow()
        }

        col_groups.update_one(
            {"_id": ObjectId(group_id)},
            {"$push": {"expenses": expense}}
        )

        flash("Expense added successfully!")
        return redirect(url_for("groups"))

    # Fetch full group details for rendering the form
    user = col_users.find_one({"name": username})
    user_groups = user.get("groups", [])
    group_details = [col_groups.find_one({"_id": ObjectId(group_id)}) for group_id in user_groups]

    return render_template('add-expense.html', groups=group_details)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if col_users.find_one({"name": username}):
            flash('Username is already in use. Please choose another one.')
            return redirect(url_for('registration'))

        col_users.insert_one({"name": username, "password": password, "groups": []})
        flash("Registration success.  Please log in")

        return redirect(url_for('login'))
    return render_template('registration.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # username within database, find matching projects then redirect
        user = col_users.find_one({"name": username, "password": password})
        if user:
            session['username'] = username
            flash("Login Success!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials, please try again.", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "success")
    return render_template("welcome.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
