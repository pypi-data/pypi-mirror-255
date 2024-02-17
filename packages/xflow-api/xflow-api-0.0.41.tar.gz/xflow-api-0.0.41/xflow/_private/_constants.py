import os
from dataclasses import dataclass


STREAM_DATA_SIZE = 52428800


@dataclass
class Actors:
    MANAGER: str = "manager"
    XFLOW_WORKER: str = "xflow_worker"


@dataclass
class RuntimeEnvType:
    EXECUTOR: str = "executor"
    CLIENT: str = "client"


@dataclass
class RequestPath:
    pipeline_export_component: str = "/api/v0/pipeline/component/export"
    pipeline_get_component: str = "/api/v0/pipeline/component"
    pipeline_exist_component: str = "/api/v0/pipeline/component/exist"
    deploy_export_converter: str = "/api/v0/inference/converter/export"
    data_list: str = "/api/v0/data/list"
    dataset_list: str = "/api/v0/feature/dataset/list"
    data_get: str = "/api/v0/data/download"
    dataset_get: str = "/api/v0/feature/dataset/download"


@dataclass
class PipelineType:
    data_pipeline: str = '1'
    experiment_pipeline: str = '2'


if os.getenv("SERVER_MODE") == 'True':
    RUNTIME_ENV = RuntimeEnvType.EXECUTOR
else:
    RUNTIME_ENV = RuntimeEnvType.CLIENT
    