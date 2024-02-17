from pydantic import BaseModel, Extra


class Metric(BaseModel):
    name: str
    value: float
    desc: str = ''

    class Config:
        extra = Extra.forbid
