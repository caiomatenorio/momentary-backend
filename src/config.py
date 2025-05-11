import os
from utils.errors.env_not_defined_error import EnvNotDefinedError
from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO

load_dotenv()


def get_env_var(key: str) -> str:
    value = os.getenv(key)

    if not value:
        raise EnvNotDefinedError(key)
    return value


app = Flask(__name__)
app.config["SECRET_KEY"] = get_env_var("SECRET_KEY")

socketio = SocketIO(app)
