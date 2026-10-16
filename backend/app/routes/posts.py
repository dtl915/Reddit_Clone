from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import Community, Post, Comment, PostVote
from sqlalchemy.orm import joinedload

bp = Blueprint("posts", __name__, url_prefix="/posts")


@bp.route("/", methods=["POST"])
@jwt_required()
def create_post():
    data = request.get_json(silent=True) or {}
    community_id = data.get("community_id")
    author_id = int(current_user.id)
    title = data.get("title")
    content = data.get("content", "")
    if not isinstance(community_id, int) or isinstance(community_id, bool):
        return jsonify({"error": "community_id is empty"}), 400
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is empty"}), 400
    if not isinstance(content, str):
        return jsonify({"error": "invalid content"}), 400
    community = Community.query.get_or_404(community_id)
    post = Post(
        community_id=community_id,
        author_id=author_id,
        title=title,
        content=content if content.strip() else None,
    )

    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201


@bp.route("/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.get_or_404(post_id)
    return jsonify(post.to_dict()), 200


@bp.route("/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    user_id = int(current_user.id)
    post = Post.get_or_404(post_id)

    if user_id != post.author_id:
        return (
            jsonify({"error": "you do not have the permission to delete this post"}),
            403,
        )

    post.delete_cascade()
    db.session.commit()
    return "", 204


@bp.route("/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    post = Post.get_or_404(post_id)
    comments = (
        Comment.query.options(joinedload(Comment.author))
        .filter_by(post_id=post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return jsonify([comment.to_dict() for comment in comments]), 200


@bp.route("/<int:post_id>/vote", methods=["POST"])
@jwt_required()
def post_vote(post_id):
    data = request.get_json(silent=True) or {}
    value = data.get("value")

    if value is None:
        return jsonify({"error": "value of this vote is missing"}), 400

    if value not in [1, 0, -1] or isinstance(value, bool) or isinstance(value, float):
        return jsonify({"error": "the value of 'value' is invalid"}), 400

    post = Post.get_or_404(post_id)
    vote = PostVote.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if vote is None:
        new_vote = PostVote(user_id=current_user.id, post_id=post_id, value=value)
        post.score += value
        db.session.add(new_vote)
        db.session.commit()
        return jsonify({"score": post.score}), 201
    else:
        diff = value - vote.value
        vote.value = value
        post.score += diff
        if vote.value == 0:
            db.session.delete(vote)
        db.session.commit()
        return jsonify({"score": post.score}), 200


@bp.route("/", methods=["GET"])
def get_recent_posts():  # limit = 25
    posts = (
        Post.query.options(joinedload(Post.community), joinedload(Post.author))
        .order_by(Post.created_at.desc())
        .limit(25)
        .all()
    )
    return jsonify([post.to_dict() for post in posts]), 200
