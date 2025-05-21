from src.singleton.app import app
from src.singleton.env import env
from src.singleton.socketio import socketio

if __name__ == "__main__":
    import eventlet

    match env.FLASK_ENV:
        case "development":
            import eventlet.wsgi  # development server
        case "production":
            import gunicorn  # production server

    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
    print("Server started.")
