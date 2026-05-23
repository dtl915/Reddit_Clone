from app import db
from datetime import datetime

class User(db.Model):
    """
    - id: user's unique id
    - username: the name of the user in the platform
    - email: the email of the user, for identity authentication
    - password_hash: hashed password
    - created_at: date the account is created
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique= True, nullable = False)
    email = db.Column(db.String, unique=True, nullable = False)
    password_hash = db.Column(db.String, nullable = False)
    created_at = db.Column(db.DateTime, default= datetime.utcnow, nullable =False)

    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "created_at":self.created_at.isoformat(),
        }
    
    def to_dict_private(self):
        return {
            **self.to_dict(),
            "email":self.email,
        }
