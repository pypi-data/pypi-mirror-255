import sys
import requests
import traceback
import json

from pydantic import BaseModel, Extra

from xflow._private._constants import RUNTIME_ENV, RuntimeEnvType
import xflow._utils.request_util as request_util

this = sys.modules[__name__]


class ClientInformation(BaseModel):
    xflow_server_url: str
    project: str
    user: str
    is_init: bool = False

    class Config:
        extra = Extra.forbid


def init():
    if RUNTIME_ENV == RuntimeEnvType.EXECUTOR:
        print("no need to init xflow on server.")
        return
    if hasattr(this, "client_info"):
        if this.client_info.is_init:
            return
    try:
        with open("/etc/xflow/config.json", 'r') as conf_file:
            conf_data = json.load(conf_file)
        # conf_data = {"PRJ_ID": "bc4ab35d-145b-4646-8636-2cc4ce0cf5e8",
        # "WRKBN_ID": "d272c93a-9289-11ee-b3ac-0242ac160002", "USER_ID": "TESTER", "WB_SERVER_URL": "https://172.20.30.157:7000"}  #dev
    except Exception as exc:
        raise RuntimeError(f"can't load client configuration: {exc.__str__()}")
    else:
        xflow_server_url = None
        # xflow_server_url = "http://172.20.40.121:8700"  # dev
        service_discovery_url = conf_data["WB_SERVER_URL"] + "/api/service?name=xflow"
        code, msg = request_util.get(url=service_discovery_url)
        if code == 0:
            xflow_server_url = msg["URL"]
        if xflow_server_url is None:
            raise InitError("can't find xflow server")
        this.client_info = ClientInformation(xflow_server_url=xflow_server_url,
                                             project=conf_data["PRJ_ID"],
                                             user=conf_data["USER_ID"],
                                             is_init=True)


class InitError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.traceback = traceback.format_exc()


def init_check() -> None:
    if hasattr(this, "client_info"):
        if not this.client_info.is_init:
            init()
            # raise RuntimeError("xflow didn't initiated. call xflow.init() before using xflow")
    else:
        init()
        # raise RuntimeError("xflow didn't initiated. call xflow.init() before using xflow")
