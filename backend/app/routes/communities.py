from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity
from app import db
from app.models import Community, User
from sqlalchemy.exc import IntegrityError
bp = Blueprint("communities", __name__, url_prefix="/communities")

@bp.route("/", methods = ["POST"])
@jwt_required()
def create_community():
    data = request.get_json(silent=True) or {}
    creator_id = get_jwt_identity()
    creator = User.query.filter_by(id = creator_id).first()
    name = data.get("name")
    description = data.get("description")

    if creator is None:
        return jsonify({"error":"account not found"}), 400

    if name is None:
        return jsonify({"error":"name cannot be empty"}), 400
    
    community = Community(name = name, description = description, creator_id = creator.id )

    try:
        db.session.add(community)
        db.session.commit()
    except IntegrityError:
        return jsonify({"error": "the name of this community already taken"}), 409
    return jsonify(community.to_dict()), 201
    

@bp.route("/", methods = ["GET"])
def list_communities():
    communities = Community.query.all()
    return jsonify([community.to_dict() for ind, community in enumerate(communities)]), 200

@bp.route("/<int:community_id>", methods=["GET"])
def get_community(community_id):
    community = Community.query.get_or_404(community_id)  
    return jsonify(community.to_dict())

@bp.route("/<int:community_id>", methods=["DELETE"])
@jwt_required()
def delete_community(community_id):
    user_id = int(get_jwt_identity())
    community = Community.query.get_or_404(community_id)

    if user_id != community.creator_id:
        return jsonify({"error":"you do not have the permission do delete this community"}), 400
    
    db.session.delete(community)
    db.session.commit()
    return "", 204