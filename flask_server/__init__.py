import logging
from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .user.services import init_app as init_user_login_services
from .user.models import db as user_db
from .auth.services import init_app as init_auth_oauth_services
from .auth import auth_bp
from .features.jobs_routes import jobs_bp
from .features.resume_tools_routes import resume_tools_bp
from .features.ai_practice_routes import ai_practice_bp


def create_app(config_class=Config):
    app = Flask("flask_server")
    app.config.from_object(config_class)

    logging.basicConfig(level=logging.INFO)

    CORS(app)

    user_db.init_app(app)
    with app.app_context():
        user_db.create_all()

    init_user_login_services(app)
    init_auth_oauth_services(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(resume_tools_bp)
    app.register_blueprint(ai_practice_bp)

    @app.route('/')
    def home():
        return jsonify({"message": "Backend is running successfully 🎉"})

    return app