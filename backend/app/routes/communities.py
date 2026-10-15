from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import Community, Post
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

bp = Blueprint("communities", __name__, url_prefix="/communities")


@bp.route("/", methods=["POST"])
@jwt_required()
def create_community():
    data = request.get_json(silent=True) or {}
    creator = current_user
    name = data.get("name")
    description = data.get("description")

    if name is None:
        return jsonify({"error": "name cannot be empty"}), 400

    community = Community(name=name, description=description, creator_id=creator.id)

    try:
        db.session.add(community)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "the name of this community already taken"}), 409
    return jsonify(community.to_dict()), 201


@bp.route("/", methods=["GET"])
def list_communities():
    communities = Community.query.all()
    return (
        jsonify([community.to_dict() for ind, community in enumerate(communities)]),
        200,
    )


@bp.route("/<int:community_id>", methods=["GET"])
def get_community(community_id):
    community = Community.get_or_404(community_id)
    return jsonify(community.to_dict())


@bp.route("/<int:community_id>", methods=["DELETE"])
@jwt_required()
def delete_community(community_id):
    user_id = int(current_user.id)
    community = Community.get_or_404(community_id)

    if user_id != community.creator_id:
        return (
            jsonify(
                {"error": "you do not have the permission to delete this community"}
            ),
            400,
        )

    for post in Post.query.filter_by(community_id=community.id):
        post.delete_cascade()

    db.session.delete(community)
    db.session.commit()
    return "", 204


@bp.route("/<int:community_id>/posts", methods=["GET"])
def get_posts(community_id):
    community = Community.get_or_404(community_id)
    posts = (
        Post.query.options(joinedload(Post.community), joinedload(Post.author))
        .filter_by(community_id=community_id)
        .order_by(Post.created_at.desc())
        .all()
    )
    return jsonify([post.to_dict() for post in posts])
