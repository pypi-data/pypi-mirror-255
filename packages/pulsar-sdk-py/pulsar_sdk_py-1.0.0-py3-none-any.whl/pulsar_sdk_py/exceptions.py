class APIError(Exception):
    message: str
    status_code: int

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(f"{message} (Status Code: {status_code})")
        self.status_code = status_code
        self.message = message
        self.name = "APIError"


class WebSocketClosed(Exception):
    pass


class SerializationError(Exception):
    pass


class WrongResponseFormat(Exception):
    pass
