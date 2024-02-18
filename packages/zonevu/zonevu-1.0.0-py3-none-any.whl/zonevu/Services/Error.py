from requests import Response
from strenum import StrEnum


class ZonevuErrorKinds(StrEnum):
    Server = 'Server'
    Client = 'Client'


class ResponseError(BaseException):
    response: Response
    message: str

    def __init__(self, r: Response):
        self.response = r
        self.message = r.reason


class ZonevuError(BaseException):
    source: any
    message: str
    kind: ZonevuErrorKinds
    status_code: int = 0        # Http code

    def __init__(self, msg: str, kind: ZonevuErrorKinds = ZonevuErrorKinds.Client, src: any = None):
        self.message = msg
        self.kind = kind
        self.source = src

    @staticmethod
    def server(r: Response) -> 'ZonevuError':
        error = ZonevuError(r.reason, ZonevuErrorKinds.Server, r)
        error.status_code = r.status_code
        return error

    @staticmethod
    def local(msg: str) -> 'ZonevuError':
        error = ZonevuError(msg, ZonevuErrorKinds.Client)
        return error
