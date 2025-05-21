from src.socket.decorator.handle_auth_namespace_connection import (
    handle_auth_namespace_connection,
)
from src.socket.decorator.handle_auth_namespace_disconnection import (
    handle_auth_namespace_disconnection,
)


def requires_auth(namespace):

    if hasattr(namespace, "on_connect") and callable(namespace.on_connect):

        @handle_auth_namespace_connection
        def wrapper(self, *args, **kwargs):
            return namespace.on_connect(self, *args, **kwargs)

        namespace.on_connect = wrapper
    else:

        @handle_auth_namespace_connection
        def on_connect(self): ...

        namespace.on_connect = on_connect

    if hasattr(namespace, "on_disconnect") and callable(namespace.on_disconnect):

        @handle_auth_namespace_disconnection
        def wrapper(self, *args, **kwargs):
            return namespace.on_disconnect(self, *args, **kwargs)

        namespace.on_disconnect = wrapper
    else:

        @handle_auth_namespace_disconnection
        def on_disconnect(self): ...

        namespace.on_disconnect = on_disconnect

    return namespace
