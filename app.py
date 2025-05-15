from src.common.blueprints.api import api
from src.common.libs.marshmallow import marshmallow
from src.common.libs.migrate import migrate
from src.common.libs.socketio import socketio
from src.common.libs.sqlalchemy import db
from src.config import create_app

app = create_app(db, migrate, socketio, marshmallow, api)

if __name__ == "__main__":
    socketio.run(app, debug=True)
    print("Server started.")
