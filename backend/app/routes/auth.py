import bcrypt as bc
from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models import User
from app import db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods = ["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not all([username, password, email]):
        return jsonify({"error":"personal information cannot be empty"}), 400

    salt = bc.gensalt()
    password_hash = bc.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    user = User(username = username, email = email, password_hash = password_hash)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"username or email already taken"}), 409

    return jsonify({"ID": user.id, "username": user.username, "email":user.email}), 201


@bp.route("/login", methods = ["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error":"email or password cannot be empty"}), 400
    
    user = User.query.filter_by(email = email).first()
    
    if user is None:
        return jsonify({"error": "the account doesn't exist"}), 401
    
    hashed_pw = user.password_hash
    if bc.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8")):
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token":token}), 200
    else:
        return jsonify({"error": "invalid password"}), 401

@bp.route("/me", methods = ["GET"])
@jwt_required()
def me():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(id = user_identity).first()
    if user is None:
        return jsonify({"error":"the account doesn't exist"}), 401
    
    return jsonify({"id":user.id, "username": user.username, "email":user.email}), 200