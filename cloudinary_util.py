import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from flask import jsonify
from pymongo import MongoClient

load_dotenv()

uri = os.environ.get("MONGODB_CONNECTION_STRING")
client = MongoClient(uri)

def upload_image_to_cloudinary(image):
    try:
        upload_response = cloudinary.uploader.upload(image)
        return upload_response.get("secure_url")
    except Exception as e:
        return jsonify({"message": str(e)})
    

def save_image_url_to_mongoDB(user_id, image_url):
    try:
        database = client.get_database("ocr-app")
        history = database.get_collection("history")
        save_response = history.insert_one({
            "user_id": user_id,
            "image_url": image_url
        })
        return jsonify({"acknowledge": save_response.acknowledged})
    except Exception as e:
        return jsonify({"error": f"Failed to save image URL: {str(e)}"})