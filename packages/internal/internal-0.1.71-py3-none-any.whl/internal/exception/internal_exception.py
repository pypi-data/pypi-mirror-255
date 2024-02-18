from fastapi import status
from .base_exception import InternalBaseException


class BadGatewayException(InternalBaseException):
    code = "error_bad_gateway"
    message = "Bad gateway"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_502_BAD_GATEWAY, self.code, _message, **kwargs)


class GatewayTimeoutException(InternalBaseException):
    code = "error_gateway_timeout"
    message = "Gateway timeout"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_504_GATEWAY_TIMEOUT, self.code, _message, **kwargs)
