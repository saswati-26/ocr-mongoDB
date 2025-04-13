from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from cloudinary_util import save_image_url_to_mongoDB, upload_image_to_cloudinary
from database import get_paginated_history, save_history
from ocr import process_image
from translation import translate_text

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"})
    user_id = get_jwt_identity()
    user_object_id = ObjectId(user_id)
    image = request.files["image"]
    try:
        image_url = upload_image_to_cloudinary(image)
        save_image_url_to_mongoDB(user_object_id, image_url)
        return jsonify({
            "message": f"User with ID {user_object_id} uploaded the image successfully!",
            "image_url": image_url
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)})

@routes_bp.route("/ocr", methods= ["POST"])
@jwt_required()
def ocr():
    image_url = request.json.get("image_url")
    user_id = get_jwt_identity()
    user_object_id = ObjectId(user_id)
    if not image_url:
        return jsonify({"error": "No image URL provided"})
    text = process_image(image_url)
    save_history(user_object_id, image_url, text)
    return jsonify({
        "extracted_text": text,
    })

@routes_bp.route("/translate", methods=["POST"])
def translate():
    data = request.json
    translated_text = translate_text(data["text"], data["target_lang"])
    return jsonify({"translated_text": translated_text})

@routes_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=3, type=int)
    return jsonify(get_paginated_history(user_id, page, page_size))
