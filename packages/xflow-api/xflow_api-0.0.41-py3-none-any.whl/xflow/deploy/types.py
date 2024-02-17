from dataclasses import dataclass
from pydantic import BaseModel, validator


@dataclass
class DataTypes:
    BOOL: str = "TYPE_BOOL"
    UINT8: str = "TYPE_UINT8"
    UINT16: str = "TYPE_UINT16"
    UINT32: str = "TYPE_UINT32"
    UINT64: str = "TYPE_UINT64"
    INT8: str = "TYPE_INT8"
    INT16: str = "TYPE_INT16"
    INT32: str = "TYPE_INT32"
    INT64: str = "TYPE_INT64"
    FP16: str = "TYPE_FP16"
    FP32: str = "TYPE_FP32"
    FP64: str = "TYPE_FP64"
    BYTES: str = "TYPE_STRING"
    BF16: str = "TYPE_BF16"


class IOSignature(BaseModel):
    name: str
    data_type: str
    dims: list

    @validator("data_type")
    def data_type_check(cls, v):
        if v not in list(DataTypes().__dict__.values()):
            raise ValueError(f"unsupported datatype {v}. use DataTypes class in xflow.deploy")
        return v

    class Config:
        extra = 'forbid'


