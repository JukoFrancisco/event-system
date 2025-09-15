import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required
)
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/eventdb")
client = MongoClient(MONGO_URI)
db = client["eventdb"]
users = db["users"]
events = db["events"]

# ---------- AUTH ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username, password = data.get("username"), data.get("password")
    if not username or not password:
        return jsonify({"message": "Missing credentials"}), 400
    if users.find_one({"username": username}):
        return jsonify({"message": "User already exists"}), 400
    users.insert_one({
        "username": username,
        "password_hash": generate_password_hash(password)
    })
    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    user = users.find_one({"username": data.get("username")})
    if user and check_password_hash(user["password_hash"], data.get("password")):
        token = create_access_token(identity=str(user["_id"]))
        return jsonify({"access_token": token}), 200
    return jsonify({"message": "Bad credentials"}), 401

# ---------- EVENTS ----------
@app.route("/events", methods=["POST"])
@jwt_required()
def create_event():
    data = request.json or {}
    result = events.insert_one({
        "name": data.get("name"),
        "date": data.get("date"),
        "registrations": []
    })
    return jsonify({
        "message": "Event created",
        "id": str(result.inserted_id)
    }), 201

@app.route("/events", methods=["GET"])
def list_events():
    output = []
    for e in events.find():
        output.append({
            "id": str(e["_id"]),
            "name": e["name"],
            "date": e.get("date"),
            "registrations": e.get("registrations", [])
        })
    return jsonify(output), 200

@app.route("/events/<event_id>/register", methods=["POST"])
@jwt_required()
def register_student(event_id):
    data = request.json or {}
    student_name = data.get("name")
    res = events.update_one(
        {"_id": ObjectId(event_id)},
        {"$push": {"registrations": {"student_name": student_name}}}
    )
    if res.matched_count == 0:
        return jsonify({"message": "Event not found"}), 404
    return jsonify({"message": "Student registered"}), 201

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


