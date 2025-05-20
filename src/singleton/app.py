from src.api.blueprint.api_bp import api_bp
from src.config import create_app
from src.singleton.db import db
from src.singleton.marshmallow import marshmallow
from src.singleton.migrate import migrate
from src.singleton.scheduler import scheduler
from src.singleton.socketio import socketio

app = create_app(db, migrate, socketio, marshmallow, scheduler, api_bp)
