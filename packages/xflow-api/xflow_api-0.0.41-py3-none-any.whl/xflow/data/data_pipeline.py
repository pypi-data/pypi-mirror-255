import requests

from xflow._utils.component import Component, ComponentTypeCode
from xflow._utils.decorators import client_method
import xflow._utils.request_util as req_util
from xflow._private._constants import RequestPath, PipelineType
from xflow._private.request_vo import ExistComponent, GetComponent
import xflow._private.client as xflow_client


@client_method
def create_component(name: str, func: callable, namespace: str = 'default',
                     description: str = '', output_names: list[str] | None = None) -> Component:
    xflow_client.init_check()
    client_info: xflow_client.ClientInformation = xflow_client.client_info
    url = client_info.xflow_server_url + RequestPath.pipeline_exist_component
    req_body = ExistComponent(PRJ_ID=client_info.project, CMPNT_NM=name, CMPNT_TYPE_CD=PipelineType.data_pipeline)
    code, msg = req_util.post(url=url, data=req_body.dict())
    if code != 0:
        raise RuntimeError("failed to read component information from server")
    if msg["EXIST"]:
        print(f"component {name} already exist. try get_component method")
        return
    return Component(name=name, func=func, namespace=namespace, desc=description, output_names=output_names,
                     component_type=PipelineType.data_pipeline)


@client_method
def get_component(name: str, revision: int | None = None):
    xflow_client.init_check()
    client_info: xflow_client.ClientInformation = xflow_client.client_info
    url = client_info.xflow_server_url + RequestPath.pipeline_get_component
    req_body = GetComponent(PRJ_ID=client_info.project, CMPNT_NM=name, CMPNT_TYPE_CD=PipelineType.data_pipeline,
                            CMPNT_RVSN=revision)
    code, msg = req_util.post(url=url, data=req_body.dict())
    if code != 0:
        raise RuntimeError("failed to get component from server")
    name = msg["NAME"]
    script = msg["SCRIPT"]
    namespace = msg["NAMESPACE"]
    desc = msg["DESC"]
    out_names = msg["OUT_NAMES"]
    if not out_names:
        out_names = None
    function_name = msg["FUNCTION_NAME"]
    try:
        exec(script)
        func = eval(function_name)
    except Exception:
        raise RuntimeError("failed to parsing component function. "
                           "check the execution environment e.g) package requirements")
    else:
        return Component(name=name, func=func, namespace=namespace, desc=desc, output_names=out_names, script=script,
                         component_type=PipelineType.data_pipeline)
