from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from blocklist import BLOCKLIST
from hash_password import hash_password
from datetime import datetime
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from bson import ObjectId


load_dotenv()

uri = os.environ.get("MONGODB_CONNECTION_STRING")
client = MongoClient(uri)

auth_bp = Blueprint('auth', __name__)

database = client.get_database("ocr-app")
users = database.get_collection("users")

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try: 
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")
        hashed_password = hash_password(password)

        if not email or not password or not username:
            return jsonify({"error": "Please fill all the details"})

        isExistingUser = users.find_one({
            "username": username
        })

        if isExistingUser:
            return jsonify({"message": "User already exists. Try a different username"})
        else:
            user_data = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "created_at": datetime.now()
            }
            response = users.insert_one(user_data)
            return jsonify({
                "acknowledge": response.acknowledged,
                "message": "User registered successfully!!"
            })
    except Exception as e:
        return jsonify({"error: ", str(e)})
    
@auth_bp.route("/login", methods = ["POST"])
def login():
    try:
        username = request.json.get("username")
        password = request.json.get("password")

        user = users.find_one({"username": username})

        if user:
            stored_hash_password = user.get("password")
            hashed_password = hash_password(password)

            if stored_hash_password == hashed_password:
                user_id = str(user["_id"])
                access_token = create_access_token(identity=user_id)
                return jsonify({
                    "message": "Login successful!",
                    "token": access_token,
                    "user_id": user_id
                    })
            else:
                return jsonify({"message": "Invalid username or password"})
        else:
            return jsonify({"message": "User does not exits. Please get yourself registered"})

    except Exception as e:
        return jsonify({"error": str(e)})
    
@auth_bp.route("/update-user", methods=["PATCH"])
@jwt_required()
def update_user():
    try:
        current_user = get_jwt_identity()
        # print(current_user)
        user_object_id = ObjectId(current_user)
        query_filter = {"_id": user_object_id}
        update_operation = {"$set":{}}

        
        if "username" in request.json:
            update_operation["$set"]["username"] = request.json.get("username")
        if "email" in request.json:
            update_operation["$set"]["email"] = request.json.get("email")
        if "password" in request.json:
            update_operation["$set"]["password"] = hash_password(request.json.get("password"))

        if not update_operation["$set"]:
            return jsonify({"message": "No fields provided for update"})
        
        update_user_response = users.update_one(query_filter, update_operation)       
        
        if update_user_response.modified_count > 0:
            return jsonify({"message": "User updated successfully"})
        elif update_user_response.matched_count == 0:
            return jsonify({
                "message": "User not found",
                "user_id": current_user
                })
        else:
            return jsonify({"message": "User data is already up-to-date"})

    except Exception as e:
        return jsonify({"error": str(e)})

@auth_bp.route("/forgot-password", methods=["PATCH"])
@jwt_required()
def forgot_password():
    try:
        current_user = get_jwt_identity()
        user_object_id = ObjectId(current_user)
        query_filter = {"_id": user_object_id}
        update_operation = {"$set":{
            "password": hash_password(request.json.get("password"))
        }}            

        update_password_response = users.update_one(query_filter, update_operation)
        
        if update_password_response.modified_count > 0:
            return jsonify({"message": "Password updated successfully"})
        elif update_password_response.matched_count == 0:
            return jsonify({"message": "Password not found"})
        else:
            return jsonify({"message": "Password is already updated"})

    except Exception as e:
        return jsonify({"error": str(e)})
     
@auth_bp.route("/delete-user", methods=["DELETE"])
@jwt_required()
def delete_user():
    try:
        current_user = get_jwt_identity()
        user_object_id = ObjectId(current_user)
        query_filter = {"_id": user_object_id}
        delete_user_response = users.delete_one(query_filter)

        if delete_user_response.deleted_count > 0:
            return jsonify({"message": "User deleted successfully!!"})
        else:
            return jsonify({"message": "User not found or could not be deleted. please try again!!"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "User logged out successfully!!"}
    except Exception as e:
        return jsonify({"error": str(e)})