from pydantic import BaseModel


class ExportComponent(BaseModel):
    PRJ_ID: str
    CMPNT_NM: str
    CMPNT_NMSPC: str
    CMPNT_RVSN_DESC: str
    CMPNT_FUNC_NM: str
    CMPNT_TYPE_CD: str
    CMPNT_IN: dict[str, dict[str, str]]
    CMPNT_OUT: dict[str, list[str | None | dict]]
    CMPNT_SCRIPT: str
    CMPNT_DESC: str
    REG_ID: str

    class Config:
        extra = 'forbid'


class ExistComponent(BaseModel):
    PRJ_ID: str
    CMPNT_NM: str
    CMPNT_TYPE_CD: str


class GetComponent(BaseModel):
    PRJ_ID: str
    CMPNT_NM: str
    CMPNT_TYPE_CD: str
    CMPNT_RVSN: int | None

    class Config:
        extra = 'forbid'


class ExportConverter(BaseModel):
    PRJ_ID: str
    CNVRT_NM: str
    DESC: str
    CNVRT_IN: list[dict]
    CNVRT_OUT: list[dict]
    CNVRT_BCKN: str
    CNVRT_SCRIPT: str
    CNVRT_PKG: list[str]
    REG_ID: str
    CNVRT_NMSPC: str
    CNVRT_RVSN_DESC: str


class SourceDataInfo(BaseModel):
    PRJ_ID: str
    DATA_NM: str


class DatasetInfo(BaseModel):
    PRJ_ID: str
    DS_NM: str
    REV: int | None
    TRIAL: int | None
    LATEST: bool = True
