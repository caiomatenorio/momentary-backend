from .config import create_app, db, socketio, ma, api_bp

app = create_app(db, socketio, ma, api_bp)

if __name__ == "__main__":
    socketio.run(app, debug=True)
    print("Server started.")
