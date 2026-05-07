from app import db
from datetime import datetime


class Comment(db.Model):

    """
    - id: unique id of this comment
    - author_id: the user id of the author
    - parent_id: the id of the comment that this comment is replying to, none if this comment is not a reply
    - post_id: the id of the post this comment is belong to
    - content: content of this comment
    - score: number of upvote - number of downvote
    - created_at: the date this comment is created
    """


    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index("ix_comments_post", "post_id"),
        db.Index("ix_comments_author_created", "author_id", "created_at"),
    )
