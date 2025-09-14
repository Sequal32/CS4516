from enum import Enum
from os import stat
import re
from typing import Dict, Optional


class RtspMethod(Enum):
    SETUP = "SETUP"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    TEARDOWN = "TEARDOWN"


class RtspStatus(Enum):
    OK = "200 OK"
    NOT_FOUND = "404 NOT FOUND"
    CONNECTION_ERROR = "500 CONNECTION ERROR"


STATUS_TO_CODE = {
    "200": RtspStatus.OK,
    "404": RtspStatus.NOT_FOUND,
    "500": RtspStatus.CONNECTION_ERROR,
}


class RtspHeader:
    version: str = "RTSP/1.0"

    def encode(self) -> str:
        raise NotImplementedError

    @staticmethod
    def decode(data: str):
        raise NotImplementedError


class RtspRequestHeader(RtspHeader):
    method: RtspMethod
    filename: str

    def __init__(self, method: RtspMethod, filename: str):
        self.method = method
        self.filename = filename

    def encode(self) -> str:
        return f"{self.method.value} {self.filename} RTSP/1.0"

    @staticmethod
    def decode(data: str):
        parts = data.split(" ")

        if len(parts) < 3 or parts[2] != "RTSP/1.0":
            raise ValueError("Invalid RTSP request line")

        return RtspRequestHeader(RtspMethod[parts[0]], parts[1])


class RtspResponseHeader(RtspHeader):
    status: RtspStatus

    def __init__(self, status: RtspStatus):
        self.status = status

    def encode(self) -> str:
        return f"RTSP/1.0 {self.status.value}"

    @staticmethod
    def decode(data: str):
        if not data.startswith("RTSP/1.0 "):
            raise ValueError("Invalid RTSP response line")

        code_str = data[len("RTSP/1.0 ") :].strip()
        code_num = code_str.split(" ")[0]

        return RtspResponseHeader(STATUS_TO_CODE[code_num])


class RtspPacket:
    headers: Dict[str, str]

    def __init__(self, header: RtspHeader):
        self.header = header
        self.headers = {}

    def set_header(self, key: str, value: object):
        self.headers[key] = str(value)

    def get_header(self, key: str) -> Optional[str]:
        return self.headers.get(key, None)


    def _encode_headers(self) -> str:
        header_str = ""
        for header in self.headers:
            header_str += f"{header}: {self.headers[header]}\n"

        return header_str

    def encode(self) -> str:
        return self.header.encode() + "\n" + self._encode_headers()

    @staticmethod
    def decode(data: str):
        raise NotImplementedError


class RtspRequest(RtspPacket):
    header: RtspRequestHeader

    def __init__(self, method: RtspMethod, filename: str):
        super().__init__(RtspRequestHeader(method, filename))

    @staticmethod
    def decode(data: str):
        lines = data.split("\n")

        header = RtspRequestHeader.decode(lines[0])
        self = RtspRequest(header.method, header.filename)

        # Parse headers
        for line in lines[1:]:
            parts = line.split(":")

            key = parts[0].strip()
            value = ":".join(parts[1:]).strip()  # In case the value contains ':'

            self.set_header(key, value)

        return self

    def method(self) -> RtspMethod:
        return self.header.method

    def filename(self) -> str:
        return self.header.filename


class RtspResponse(RtspPacket):
    header: RtspResponseHeader

    def __init__(self, code: RtspStatus):
        super().__init__(RtspResponseHeader(code))

    @staticmethod
    def decode(data: str):
        lines = data.split("\n")

        header = RtspResponseHeader.decode(lines[0])
        self = RtspResponse(header.status)

        # Parse headers
        for line in lines[1:]:
            parts = line.split(":")

            key = parts[0].strip()
            value = ":".join(parts[1:]).strip()  # In case the value contains ':'

            self.set_header(key, value)

        return self

    def status(self) -> RtspStatus:
        return self.header.status
