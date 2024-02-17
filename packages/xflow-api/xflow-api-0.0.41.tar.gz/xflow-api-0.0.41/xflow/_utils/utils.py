from typing import Callable
import struct

import ray

from xflow._private._constants import Actors, RuntimeEnvType, RUNTIME_ENV, RequestPath
from xflow._utils.decorators import executor_method
import xflow._private.client as xflow_client


class PacketHeader:
    def __init__(self, header_type: bytes):
        self.header_length: int = 11 # un short: 2
        self.header_type: bytes = header_type   # char: 1
        self.contents_length: int = 0   # un long long: 8

    def create_packet(self, data: bytes):
        self.contents_length = len(data)
        header = struct.pack("=HcQ", self.header_length, self.header_type, self.contents_length)
        return header + data


class RollbackContext:
    def __init__(self, task: Callable, **kwargs):
        self._task: Callable = task
        self._args: dict = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._task(**self._args)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def get_project() -> str:
    project = None
    if RUNTIME_ENV == RuntimeEnvType.EXECUTOR:
        actor_id = ray.get_runtime_context().get_actor_id()
        manager_actor = ray.get_actor(Actors.MANAGER)
        owner_actor = ray.get(manager_actor.get_pool_actor_owner.remote(actor_id))
        owner_actor = ray.get_actor(owner_actor)
        project, pipeline, rev, trial, reg_id = ray.get(owner_actor.get_pipeline_info.remote())
    elif RUNTIME_ENV == RuntimeEnvType.CLIENT:
        xflow_client.init_check()
        client_info: xflow_client.ClientInformation = xflow_client.client_info
        project = client_info.project
    if project is None:
        raise RuntimeError(f"failed to get project id from runtime environment")
    return project


@executor_method
def get_pipeline_info() -> tuple[str, str, int, int, str]:
    project = None
    pipeline = None
    rev = None
    trial = None
    reg_id = None
    if RUNTIME_ENV == RuntimeEnvType.EXECUTOR:
        actor_id = ray.get_runtime_context().get_actor_id()
        manager_actor = ray.get_actor(Actors.MANAGER)
        owner_actor = ray.get(manager_actor.get_pool_actor_owner.remote(actor_id))
        owner_actor = ray.get_actor(owner_actor)
        project, pipeline, rev, trial, reg_id = ray.get(owner_actor.get_pipeline_info.remote())
    if pipeline is None or rev is None or trial is None:
        raise RuntimeError(f"failed to get pipeline info from runtime environment")
    return project, pipeline, rev, trial, reg_id


def get_data_download_url() -> str:
    download_url = None
    if RUNTIME_ENV == RuntimeEnvType.EXECUTOR:
        manager_actor = ray.get_actor(Actors.MANAGER)
        download_url = ray.get(manager_actor.get_data_download_url.remote())
    elif RUNTIME_ENV == RuntimeEnvType.CLIENT:
        xflow_client.init_check()
        client_info: xflow_client.ClientInformation = xflow_client.client_info
        download_url = client_info.xflow_server_url + RequestPath.data_get
    if download_url is None:
        raise RuntimeError(f"failed to get download url from runtime environment")
    return download_url


def get_dataset_download_url() -> str:
    download_url = None
    if RUNTIME_ENV == RuntimeEnvType.EXECUTOR:
        manager_actor = ray.get_actor(Actors.MANAGER)
        download_url = ray.get(manager_actor.get_dataset_download_url.remote())
    elif RUNTIME_ENV == RuntimeEnvType.CLIENT:
        xflow_client.init_check()
        client_info: xflow_client.ClientInformation = xflow_client.client_info
        download_url = client_info.xflow_server_url + RequestPath.dataset_get
    if download_url is None:
        raise RuntimeError(f"failed to get download url from runtime environment")
    return download_url


@executor_method
def get_dataset_upload_url() -> str:
    upload_url = None
    if RUNTIME_ENV == RuntimeEnvType.EXECUTOR:
        manager_actor = ray.get_actor(Actors.MANAGER)
        upload_url = ray.get(manager_actor.get_dataset_upload_url.remote())
    if upload_url is None:
        raise RuntimeError(f"failed to get download url from runtime environment")
    return upload_url



