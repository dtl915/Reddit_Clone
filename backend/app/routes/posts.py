from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Community, Post, User, Comment
from sqlalchemy.exc import IntegrityError

bp = Blueprint("posts",__name__, url_prefix="/posts")

@bp.route("/", methods = ["POST"])
@jwt_required()
def create_post():
    data = request.get_json(silent=True) or {}
    community_id = data.get("community_id")
    author_id = int(get_jwt_identity())
    title = data.get("title")
    content = data.get("content")
    if community_id is None:
        return jsonify({"error":'community_id is empty'}), 400
    if author_id is None:
        return jsonify({"error":'author_id is empty'}), 400
    if title is None:
        return jsonify({"error":'title is empty'}),400

    author = User.query.get_or_404(author_id)
    community = Community.query.get_or_404(community_id)
    post = Post(community_id = community_id, author_id = author_id, title=title, content = content)

    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 200

@bp.route("/<int:post_id>", methods = ["GET"])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict()), 200

@bp.route("/<int:post_id>", methods = ["DELETE"])
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)

    if user_id != post.author_id:
        return jsonify({"error", "you do not have the permission to delete this post"}), 400
    
    db.session.delete(post)
    db.session.commit()
    return "", 204


@bp.route("/<int:post_id>/comments", methods = ["GET"])
def get_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id = post_id).order_by(Comment.created_at.asc()).all()
    return jsonify([comment.to_dict() for comment in comments]), 200
    