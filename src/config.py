from typing import Callable, Union

from flask import Blueprint, Flask
from flask_apscheduler import APScheduler
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from src.singleton.env import env


def create_app(
    db: SQLAlchemy,
    migrate: Migrate,
    socketio: SocketIO,
    marshmallow: Marshmallow,
    scheduler: APScheduler,
    bp: Blueprint,
    error_handlers: dict[Union[type[Exception], int], Callable],
    namespaces: dict[str, type],
) -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = env.DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = env.SECRET_KEY
    app.config["SCHEDULER_API_ENABLED"] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    marshmallow.init_app(app)
    scheduler.init_app(app)

    # Start CRON jobs
    scheduler.start()

    # Register blueprints
    app.register_blueprint(bp)

    # Register API error handlers
    for exception_or_code, handler in error_handlers.items():
        app.register_error_handler(exception_or_code, handler)

    # Register namespaces
    for path, namespace in namespaces.items():
        socketio.on_namespace(namespace(path))

    return app
