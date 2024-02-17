import os
import shutil
import csv
import sys

from tqdm import tqdm
import requests
import struct
import pickle
from typing import Optional, Any
from pathlib import Path

from pydantic import BaseModel

from xflow._private.request_vo import SourceDataInfo
from xflow._private._constants import RequestPath
from xflow._private._types import DataSourceType, StreamedDataInfo
from xflow._utils import request_util
from xflow._utils.utils import get_project, get_data_download_url, RollbackContext
from xflow._utils.decorators import client_method
import xflow._private.client as xflow_client


@client_method
def list_data():
    xflow_client.init_check()
    client_info: xflow_client.ClientInformation = xflow_client.client_info
    project = client_info.project
    download_url = client_info.xflow_server_url + RequestPath.data_list
    url = download_url + f"?project={project}"
    code, msg = request_util.get(url=url)
    if code != 0:
        raise RuntimeError(msg)
    return msg["DATAS"]


class DownloadSteps(BaseModel):
    file_dir: str | None = None
    file_path: str | None = None
    file_io: Any = None
    progress: Any = None
    is_done: bool = False


def get_data(name: str):
    project = get_project()
    download_url = get_data_download_url()
    req_data = SourceDataInfo(PRJ_ID=project, DATA_NM=name).dict()
    download_steps = DownloadSteps()
    data_info = None
    csv_writer = None
    rows = 0
    args = {"url": download_url, "json": req_data, "stream": True}
    if "VERIFY_SSL" in os.environ:
        if not bool(int(os.environ["VERIFY_SSL"])):
            args["verify"] = False
    with requests.post(**args) as req:
        with RollbackContext(task=clear_get_data, steps=download_steps):
            for chunk in req.iter_content(chunk_size=None):
                if chunk is None:
                    raise RuntimeError
                header_len = struct.unpack('H', chunk[:2])[0]
                header = chunk[:header_len]
                data = chunk[header_len:]
                header = struct.unpack("=HcQ", header)
                header_type = header[1]
                contents_length = header[2]
                if header_type == b'0':
                    if data_info is None:
                        raise RuntimeError
                    if data_info.SOURCE == DataSourceType.FILE:
                        download_steps.file_io.write(data)
                        download_steps.progress.update(contents_length)
                    elif data_info.SOURCE == DataSourceType.TABLE:
                        data = pickle.loads(data)
                        if isinstance(data, tuple):
                            data = [data]
                        csv_writer.writerows(data)
                        rows += len(data)
                        print(f"read rows: {rows}", end="\r", flush=True)
                elif header_type == b'1':
                    if data_info is not None:
                        raise RuntimeError
                    data_info = StreamedDataInfo(**pickle.loads(data))
                    data_path = f"{str(Path.home())}/datas/{data_info.ID}"
                    if not os.path.exists(data_path):
                        os.makedirs(data_path)
                    download_steps.file_dir = data_path
                    data_path = f"{data_path}/{data_info.FILE_NAME}"
                    download_steps.file_path = data_path
                    if data_info.SOURCE == DataSourceType.TABLE:
                        download_steps.file_io = open(data_path, "w", newline='')
                        csv_writer = csv.writer(download_steps.file_io, delimiter=",")
                    else:
                        download_steps.file_io = open(data_path, "wb")
                    if data_info.SIZE != -1:
                        download_steps.progress = tqdm(total=data_info.SIZE, initial=0, ascii=True, file=sys.stdout)
            download_steps.is_done = True
    return download_steps.file_path


def clear_get_data(steps: DownloadSteps):
    if steps.file_io is not None:
        steps.file_io.close()
    if steps.progress is not None:
        steps.progress.close()
    if not steps.is_done:
        if steps.file_dir is not None:
            shutil.rmtree(steps.file_path, ignore_errors=True)


def read_sql(data_name: str, select: Optional[list[str]], where: Optional[list[str]] = None):
    pass
