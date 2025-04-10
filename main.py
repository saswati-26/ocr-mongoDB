from flask import Blueprint, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.environ.get("MONGODB_CONNECTION_STRING")
client = MongoClient(uri)

main_bp = Blueprint("main", __name__)

@main_bp.route("/movie", methods=["GET"])
def main():
    try:
        database = client.get_database("sample_mflix")
        movies = database.get_collection("movies")
        
        query = {"title": "Back to the Future"}
        movie = movies.find_one(query)
        # print((movie))

        if movie:
            movie["_id"] = str(movie["_id"])
            return jsonify(movie)
        else:
            return jsonify({"message": "Movie 'Back to the Future' not found"}), 404

    except Exception as e:
        print(f"An exception has raised: {e}")

    finally:
        client.close()
