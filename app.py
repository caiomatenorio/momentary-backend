from src.singleton.app import app
from src.singleton.env import env
from src.singleton.socketio import socketio

if __name__ == "__main__":
    socketio.run(
        app,
        debug=(env.FLASK_ENV == "development"),
        host="0.0.0.0",
        port=5000,
    )
    print("Server started.")
