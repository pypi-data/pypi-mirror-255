from sdclient.requests import SDRequest


class SDCallError(Exception):
    def __init__(self, message: str, endpoint_name: str, params: SDRequest):
        super().__init__()
        self._message = message
        self._endpoint_name = endpoint_name
        self._params = params

    def __str__(self) -> str:
        return f"{self._message}: endpoint={self._endpoint_name} params={self._params}"

    @property
    def message(self) -> str:
        return self._message


class SDHTTPStatusError(SDCallError):
    def __init__(
        self,
        message: str,
        endpoint_name: str,
        params: SDRequest,
        status: int,
        text: str,
    ):
        super().__init__(message, endpoint_name, params)
        self._status = status
        self._text = text

    def __str__(self) -> str:
        return f"{super().__str__()} returned HTTP status {self._status} ({self._text})"

    @property
    def text(self):
        return self._text


class SDParseResponseError(SDCallError):
    pass
