from src.blueprints.api import api
from src.config import create_app
from src.libs.marshmallow import marshmallow
from src.libs.migrate import migrate
from src.libs.socketio import socketio
from src.libs.sqlalchemy import db

app = create_app(db, migrate, socketio, marshmallow, api)

if __name__ == "__main__":
    socketio.run(app, debug=True)
    print("Server started.")
