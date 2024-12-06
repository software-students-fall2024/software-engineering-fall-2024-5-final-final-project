from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId  # To handle MongoDB ObjectIds
import os
import bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB Connection
uri = "mongodb+srv://hugobray01:AmosBloomberg@splitsmart.ursnd.mongodb.net/?retryWrites=true&w=majority&appName=SplitSmart"
client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client["SplitSmart"]
col_users = mydb["USERS"]
col_groups = mydb["GROUPS"]

# Test Connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")


@app.route('/')
def base():
    return render_template("welcome.html")


@app.route('/main')
def home():
    if 'username' not in session:
        flash("Not logged in. Please log in first", "error")
        return redirect(url_for("login"))
    return render_template('home.html', username=session['username'])


@app.route('/groups')
def groups():
    if 'username' not in session:
        flash("Not logged in. Please log in first", "error")
        return redirect(url_for("login"))

    username = session['username']
    user = col_users.find_one({"name": username})
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("home"))

    user_groups = user.get("groups", [])
    group_details = []

    # Fetch group details
    for group_id in user_groups:
        group = col_groups.find_one({"_id": group_id})
        if group:
            group_details.append({
                "group_name": group["group_name"],
                "group_members": [member["name"] for member in group["group_members"]],
                "group_id": group["_id"]
            })

    return render_template('groups.html', groups=group_details)


@app.route('/create-group', methods=["GET", "POST"])
def create_group():
    if 'username' not in session:
        flash("Not logged in. Please log in first", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        group_name = request.form.get("group_name")
        members = request.form.get("members").split(",")

        if not group_name or not members:
            flash("Group name and at least one member are required.", "error")
            return redirect(url_for("create_group"))

        # Fetch user IDs for members
        member_objects = []
        for member_name in members:
            user = col_users.find_one({"name": member_name.strip()})
            if user:
                member_objects.append({"user_id": user["_id"], "name": user["name"]})
            else:
                flash(f"User '{member_name.strip()}' does not exist.", "error")
                return redirect(url_for("create_group"))

        current_user = col_users.find_one({"name": session['username']})
        if current_user and current_user["_id"] not in [m["user_id"] for m in member_objects]:
            member_objects.append({"user_id": current_user["_id"], "name": current_user["name"]})

        # Generate unique group ID
        new_group_id = str(ObjectId())
        new_group = {
            "_id": new_group_id,
            "group_name": group_name,
            "group_members": member_objects,
            "expenses": []
        }

        col_groups.insert_one(new_group)

        # Add group to users' group lists
        for member in member_objects:
            col_users.update_one(
                {"_id": member["user_id"]},
                {"$addToSet": {"groups": new_group_id}}
            )

        flash(f"Group '{group_name}' created successfully!", "success")
        return redirect(url_for("groups"))

    return render_template("create-groups.html")


@app.route('/group/<group_id>')
def group_details(group_id):
    if 'username' not in session:
        flash("Not logged in. Please log in first", "error")
        return redirect(url_for("login"))

    try:
        # Fetch group details
        group = col_groups.find_one({"_id": group_id})
        if not group:
            flash("Group not found.", "error")
            return redirect(url_for("groups"))

        group_name = group.get("group_name", "Unnamed Group")
        group_members = group.get("group_members", [])
        expenses = group.get("expenses", [])

        detailed_expenses = []
        for expense in expenses:
            # Fetch payer's name
            paid_by_user = col_users.find_one({"_id": ObjectId(expense["paid_by"])})
            paid_by_name = paid_by_user["name"] if paid_by_user else "Unknown"

            # Handle missing 'split_among' gracefully
            split_among = expense.get("split_among", {})  # Default to an empty dictionary if key is missing
            split_among_detailed = {
                col_users.find_one({"_id": ObjectId(user_id)})["name"] if col_users.find_one({"_id": ObjectId(user_id)}) else "Unknown": share
                for user_id, share in split_among.items()
            }

            detailed_expenses.append({
                "expense_id": expense.get("expense_id"),
                "description": expense.get("description"),
                "amount": expense.get("amount"),
                "paid_by": paid_by_name,
                "split_among": split_among_detailed
            })

        return render_template(
            'group-details.html',
            group_name=group_name,
            group_members=group_members,
            expenses=detailed_expenses
        )

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("groups"))


@app.route('/add-expense', methods=["GET", "POST"])
def add_expense():
    if 'username' not in session:
        flash("Not logged in. Please log in first", "error")
        return redirect(url_for("login"))

    username = session['username']
    user = col_users.find_one({"name": username})
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("groups"))

    if request.method == "POST":
        try:
            group_id = request.form.get("group_id")
            description = request.form.get("description")
            amount = float(request.form.get("amount"))
            paid_by = ObjectId(request.form.get("paid_by"))
            split_with = request.form.getlist("split_with[]")
            percentages = [float(p) for p in request.form.get("percentages").split(",")]

            # Validate percentages
            if len(percentages) != len(split_with) or sum(percentages) != 1.0:
                flash("Split percentages must match members and total 1.0.", "error")
                return redirect(url_for("add_expense"))

            # Prepare split_among with string keys
            split_among = {
                str(ObjectId(split_with[i])): round(percentages[i] * amount, 2)
                for i in range(len(split_with))
            }

            # Create the expense document
            expense_id = str(ObjectId())
            expense = {
                "expense_id": expense_id,
                "description": description,
                "amount": amount,
                "paid_by": str(paid_by),
                "split_among": split_among  # Ensure this field is always present
            }

            # Add the expense to the group
            col_groups.update_one({"_id": group_id}, {"$push": {"expenses": expense}})
            flash("Expense added successfully!", "success")
            return redirect(url_for("group_details", group_id=group_id))

        except Exception as e:
            flash(f"Error adding expense: {str(e)}", "error")
            return redirect(url_for("add_expense"))

    user_groups = user.get("groups", [])
    group_details = [col_groups.find_one({"_id": group_id}) for group_id in user_groups]
    return render_template('add-expense.html', groups=group_details)

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if col_users.find_one({"name": username}):
            flash("Username already in use.", "error")
            return redirect(url_for("registration"))
            
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        col_users.insert_one({"name": username, "password": hashed_password, "groups": []})
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = col_users.find_one({"name": username, "password": password})
        if user:
            
            stored_password=user['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                session["username"] = username
                flash("Login successful!", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid password. Please try again", "error")
        else:
            flash("Username not found. Please register account with username.", "error")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("base"))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
