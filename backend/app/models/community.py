from app import db
from datetime import datetime

class Community(db.Model):

    """
    - id: the unique id of this community
    - name: the name of this community
    - description: a brief description of this community
    - creator_id: the id of the user who created this community
    - created_at: the date that this community is being created
    """

    __tablename__ = "communities"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column (db.String, nullable = False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    created_at = db.Column(db.DateTime, default= datetime.utcnow, nullable= False)


