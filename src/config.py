from flask import Blueprint, Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError

from .common.exceptions.http_exception import HttpException
from .env import env
from .error_handler import handle_http_exception, handle_validation_error


def create_app(
    db: SQLAlchemy,
    migrate: Migrate,
    socketio: SocketIO,
    marshmallow: Marshmallow,
    bp: Blueprint,
) -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = env.DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = env.SECRET_KEY

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    marshmallow.init_app(app)
    app.register_blueprint(bp)

    # Register error handlers
    app.register_error_handler(HttpException, handle_http_exception)
    app.register_error_handler(ValidationError, handle_validation_error)

    return app
