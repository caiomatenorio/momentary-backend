from src.blueprints.api import api
from src.config import create_app
from src.libs.marshmallow import marshmallow
from src.libs.migrate import migrate
from src.libs.scheduler import scheduler
from src.libs.socketio import socketio
from src.libs.sqlalchemy import db

app = create_app(db, migrate, socketio, marshmallow, scheduler, api)
