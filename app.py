from datetime import timedelta
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from auth import auth_bp
from main import main_bp
import os

app = Flask(__name__)
jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=4)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "API is running"}), 200

app.register_blueprint(main_bp, url_prefix="/main")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)