from flask import request
from flask_socketio import emit, send

from ..libs.socketio import socketio


@socketio.on("connect")
def connect():
    print("Connected to test namespace")
    print(f"Sid: {request.sid}")
    send("hello")


@socketio.on("message")
def test(data, auth):
    print("Test event received")
    send(f"tested {data}, {auth}")
