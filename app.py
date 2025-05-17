if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    from src.app_instance import app, socketio

    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
    print("Server started.")
