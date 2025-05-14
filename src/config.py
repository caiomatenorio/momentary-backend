import os
from .utils.errors.env_not_defined_error import EnvNotDefinedError
from dotenv import load_dotenv
from flask import Flask, Blueprint
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_marshmallow import Marshmallow
from .utils.exceptions.http_exception import HttpException
from .error_handler import handle_http_exception, handle_validation_error
from marshmallow import ValidationError

load_dotenv()

def get_env_var(key: str) -> str:
    value = os.getenv(key)

    if not value:
        raise EnvNotDefinedError(key)

    return value


def create_app(db: SQLAlchemy, socketio: SocketIO, ma: Marshmallow, bp: Blueprint) -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = get_env_var("DB_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = get_env_var("SECRET_KEY")

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)
    ma.init_app(app)
    app.register_blueprint(bp)

    # Register error handlers
    app.register_error_handler(HttpException, handle_http_exception)
    app.register_error_handler(ValidationError, handle_validation_error)

    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created.")

    return app


# SQLAlchemy
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

# SocketIO
socketio = SocketIO()

# Marshmallow
ma = Marshmallow()

# Blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")