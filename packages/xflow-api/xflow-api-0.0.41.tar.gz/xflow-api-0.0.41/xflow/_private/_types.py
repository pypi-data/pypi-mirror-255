from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class PacketHeaderType:
    DATA: bytes = b'0'
    DATA_INFO: bytes = b'1'
    SUCCESS: bytes = b'2'
    FAIL: bytes = b'3'
    EOF: bytes = b'4'


@dataclass
class DataSourceType:
    FILE: str = "STORAGE"
    TABLE: str = "DB"


class StreamedDataInfo(BaseModel):
    ID: str
    DATA_NAME: str
    FILE_NAME: str
    SIZE: int
    SOURCE: str


class StreamedDataSetInfo(BaseModel):
    ID: str
    SIZE: int
