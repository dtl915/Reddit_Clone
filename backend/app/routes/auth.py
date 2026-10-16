import bcrypt as bc
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    current_user,
)
from sqlalchemy.exc import IntegrityError
from app.models import User
from app import db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    payload = [username, password, email]

    if (
        username is None
        or password is None
        or email is None
        or not all([isinstance(field, str) and field.strip() for field in payload])
    ):
        return jsonify({"error": "personal information cannot be empty"}), 400

    username = username.strip()
    email = email.strip()

    salt = bc.gensalt(rounds=current_app.config["BCRYPT_ROUNDS"])
    password_hash = bc.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    user = User(username=username, email=email, password_hash=password_hash)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "username or email already taken"}), 409

    return jsonify({"id": user.id, "username": user.username, "email": user.email}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    payload = [email, password]

    if (
        password is None
        or email is None
        or not all([isinstance(field, str) and field.strip() for field in payload])
    ):
        return jsonify({"error": "email or password cannot be empty"}), 400

    user = User.query.filter_by(email=email.strip()).first()

    if user is None:
        return jsonify({"error": "invalid email or password"}), 401

    hashed_pw = user.password_hash
    if bc.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8")):
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token}), 200
    else:
        return jsonify({"error": "invalid email or password"}), 401


@bp.route("/me", methods=["GET"])
@jwt_required()
def me():

    return (
        jsonify(
            {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
            }
        ),
        200,
    )
