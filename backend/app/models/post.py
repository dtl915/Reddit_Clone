from app import db 
from datetime import datetime

class Post(db.Model):

    """
    - id: unique id of this post
    - community_id: the id of the community this post belongs to 
    - author_id: the user id of the author
    - title: title of this post, not nullable
    - content: content of this post, is nullable
    - score: the number of upvotes - the number of downvotes of this post
    - created_at: the date of this post is being created
    """

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("communities.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable =False)
    title = db.Column(db.String, nullable =False)
    content = db.Column(db.Text)
    score = db.Column(db.Integer, default = 0, nullable=False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index("ix_posts_community_created", "community_id","created_at"),
        db.Index("ix_posts_community_score","community_id","score"),
        db.Index("ix_posts_author_created", "author_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id":self.id,
            "community_id":self.community_id,
            "author_id":self.author_id,
            "title":self.title,
            "content":self.content,
            "score":self.score,
            "created_at":self.created_at,
        }