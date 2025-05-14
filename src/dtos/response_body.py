from flask import Response

class ResponseBody:
    status_code: int
    message: str
    
    def to_response(self) -> tuple[Response, int]:
        raise NotImplementedError("Subclasses must implement this method")