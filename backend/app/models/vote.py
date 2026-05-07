from app import db
from datetime import datetime

class PostVote(db.Model):
    """
    - user_id: id of the user who voted
    - post_id: id of the post being voted
    - value: +1 means an up vote, -1 means a down vote
    - voted_at: date the user voted
    """
    __tablename__ = "post_votes"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CommentVote(db.Model):
    """
    - user_id: id of the user who voted
    - comment_id: id of the comment being voted
    - value: +1 means an up vote, -1 means a down vote
    - voted_at: date the user voted
    """
    __tablename__ = "comment_votes"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)