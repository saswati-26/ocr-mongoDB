from datetime import datetime
import os
from bson import ObjectId
from flask import jsonify
from pymongo import MongoClient

uri = os.environ.get("MONGODB_CONNECTION_STRING")
client = MongoClient(uri)

database = client.get_database("ocr-app")
history = database.get_collection("history")

def save_history(user_id, image_url, extracted_text):
    try:
        save_history_response = history.insert_one({
            "user_id": user_id,
            "image_url": image_url,
            "extracted_text": extracted_text,
            "created_at": datetime.now()
        })
        return jsonify({"acknowledge": save_history_response.acknowledged})
    except Exception as e:
        return jsonify({"error": str(e)})

def get_paginated_history(user_id, page, page_size):
    offset = (page - 1) * page_size
    user_object_id = ObjectId(user_id)
    history_activities = list(history.find({"user_id": user_object_id}).sort("created_at", -1).skip(offset).limit(page_size))
    serialized_history = []
    for activity in history_activities:
        serialized_activity = {}
        for key, value in activity.items():
            if isinstance(value, ObjectId):
                serialized_activity[key] = str(value)
            else:
                serialized_activity[key] = value
        serialized_history.append(serialized_activity)
    return serialized_history
