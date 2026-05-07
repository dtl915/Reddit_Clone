from app import db
from datetime import datetime

class ViewHistory(db.Model):

    """
    - id: the unique id of this entry
    - user_id: the user id of the user who viewed the post
    - post_id: the id of the post that is being viewed
    - viewed_at: the date the post is being viewed
    """

    __tablename__ = "view_history"

    id=  db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, default = datetime.utcnow, nullable=False)

class SavedPost(db.Model):

    """
    - user_id: the user who saved the post
    - post_id: the post being saved
    - saved_at: the date that the post is being saved
    """

    __tablename__ = "saved_posts"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    post_id = db.Column (db.Integer, db.ForeignKey("posts.id"), primary_key=True)
    saved_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

class HiddenPost(db.Model):

    """
    - user_id: the user who hide the post
    - post_id: the post being hidden
    - hidden_at: the date that the post is being hidden
    """

    __tablename__ = "hidden_posts"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    post_id = db.Column (db.Integer, db.ForeignKey("posts.id"), primary_key=True)
    hidden_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

