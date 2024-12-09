"""
This file will contain the interactions with the database.
"""

from pymongo import MongoClient, errors

def update_bal(user: str, newBal: float, win: bool, game: str):
    #maybe add admin tester
    try:
        client = MongoClient("mongodb://db:27017/")
        print("Connected to MongoDB successfully.")
    except errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return "$$$"
    
    diff = 1 if win else 0
    gamewin = "cwins" if (game == "craps") else "bwins"
    gametotal = "ctot" if (game == "craps") else "btot"
    collect = client["casinodb"]["userbals"]
    if collect.count_documents({"user": user}) != 0:
        collect.update_one({"user": user}, {
            "$set" :{
            "balance": newBal
            },
            "$inc": {
                gamewin: diff,
                gametotal: 1
            }
        })
    else: 
        if game == "craps":
            collect.insert_one({
                "user": user,
                "balance": newBal,
                "cwins": diff,
                "ctot": 1,
                "bwins": 0,
                "btot": 0
            })
        elif game == "blackjack": 
            collect.insert_one({
                "user": user,
                "balance": newBal,
                "cwins": 0,
                "ctot": 0,
                "bwins": diff,
                "btot": 1
            })
        else:  # just set up an account
            collect.insert_one({
                "user": user,
                "balance": newBal,
                "cwins": 0,
                "ctot": 0,
                "bwins": 0,
                "btot": 0
            })

def get_bal(user):
    try:
        client = MongoClient("mongodb://db:27017/")
        print("Connected to MongoDB successfully.")
    except errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return "$$$"
    
    collect = client["casinodb"]["userbals"]
    bal = collect.find_one({"user": user})["balance"]
    return float(bal)

def register_user(user, passw):
    try:
        client = MongoClient("mongodb://db:27017/")
        print("Connected to MongoDB successfully.")
    except errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return "$$$"
    
    collect = client["casinodb"]["guests"]
    collect.insert_one({
        "user": user,
        "pass": passw
    })
    update_bal(user, 1000, True, "reg")

def get_users():
    try:
        client = MongoClient("mongodb://db:27017/")
        print("Connected to MongoDB successfully.")
    except errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return "$$$"
    
    collect = client["casinodb"]["guests"]
    all_u = collect.find()
    userdict = {}
    for u in all_u:
        userdict[u["user"]] = {"password": u["pass"]}
    return userdict
    