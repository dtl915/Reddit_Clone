from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def import_bp(app):
    from app import models  # noqa: F401
    from app.routes import auth_bp
    from app.routes import communities_bp
    from app.routes import posts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(communities_bp)
    app.register_blueprint(posts_bp)



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"error": "authentication required"}), 401


    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "invalid token"}), 401


    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "token expired"}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error":"not found"}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error":"method not allowed"}), 405

    import_bp(app)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
