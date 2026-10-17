from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, current_user
from app.models import User, Post, Comment, CommentVote
from app import db

bp = Blueprint("comments", __name__, url_prefix="/comments")


@bp.route("/", methods=["POST"])
@jwt_required()
def create_comment():
    data = request.get_json(silent=True) or {}
    author_id = int(current_user.id)
    parent_id = data.get("parent_id")
    post_id = data.get("post_id")
    content = data.get("content")

    if not isinstance(post_id, int) or isinstance(post_id, bool):
        return jsonify({"error": "post_id cannot be empty"}), 400
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "content cannot be empty"}), 400

    content = content.strip()

    post = Post.get_or_404(post_id)
    if parent_id is not None:
        parent = Comment.get_or_404(comment_id=parent_id)
        if post_id != parent.post_id:
            return jsonify({"error": "invalid parent_id or post_id"}), 400

    comment = Comment(
        author_id=author_id, parent_id=parent_id, post_id=post_id, content=content
    )

    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201


@bp.route("/<int:comment_id>", methods=["GET"])
def get_comment(comment_id):
    comment = Comment.get_or_404(comment_id)
    return jsonify(comment.to_dict()), 200


@bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    comment = Comment.get_or_404(comment_id)
    user_id = int(current_user.id)

    if user_id != comment.author_id:
        return (
            jsonify({"error": "you do not have the permission to delete this comment"}),
            403,
        )

    comment.content = "[Comment Deleted]"
    db.session.commit()
    return "", 204


@bp.route("/<int:comment_id>/vote", methods=["POST"])
@jwt_required()
def comment_vote(comment_id):
    data = request.get_json(silent=True) or {}
    value = data.get("value")

    if value is None:
        return jsonify({"error": "value of this vote is missing"}), 400

    if int(value) not in [1, 0, -1]:
        return jsonify({"error": "the value of 'value' is invalid"}), 400

    comment = Comment.get_or_404(comment_id)

    if comment.content == "[Comment Deleted]":
        return jsonify({"error": "cannot vote for a deleted comment"}), 400

    user_id = int(current_user.id)
    vote = CommentVote.query.filter_by(user_id=user_id, comment_id=comment_id).first()

    if vote is None:
        new_vote = CommentVote(user_id=user_id, comment_id=comment_id, value=value)
        comment.score += value
        db.session.add(new_vote)
        db.session.commit()
        return jsonify({"score": comment.score}), 201
    else:

        diff = value - vote.value
        vote.value = value
        comment.score += diff
        if vote.value == 0:
            db.session.delete(vote)
        db.session.commit()
        return jsonify({"score": comment.score}), 200
