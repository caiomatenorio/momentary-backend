from .config import create_app
from .common.libs.sqlalchemy import db
from .common.libs.socketio import socketio
from .common.libs.marshmallow import marshmallow
from .common.blueprints.api import api

app = create_app(db, socketio, marshmallow, api)

if __name__ == "__main__":
    socketio.run(app, debug=True)
    print("Server started.")
