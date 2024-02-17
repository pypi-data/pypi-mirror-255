from xflow.deploy._util import validate_converter_script
from xflow.deploy.types import IOSignature
import xflow._private.client as xflow_client
import xflow._utils.request_util as req_util
from xflow._private._constants import RequestPath
import xflow._private.request_vo as req_vo


class Converter:
    def __init__(self, name: str, script: str, input_signature: list[IOSignature], backend: str,
                 output_signature: list[IOSignature], requirements: list[str], namespace: str, description: str = ''):
        self.__description: str = description
        self.__name: str = name
        self.__script: str = script
        self.__input_signature: list[IOSignature] = input_signature
        self.__output_signature: list[IOSignature] = output_signature
        self.__requirements: list[str] = requirements
        self.__namespace: str = namespace
        self.__backend: str = backend
        self.__validate_args()

    def export(self, description: str):
        print(f"exporting...")
        xflow_client.init_check()
        client_info: xflow_client.ClientInformation = xflow_client.client_info
        url = client_info.xflow_server_url + RequestPath.deploy_export_converter
        CNVRT_IN = []
        CNVRT_OUT = []
        for _ in self.__input_signature:
            CNVRT_IN.append(_.dict())
        for _ in self.__output_signature:
            CNVRT_OUT.append(_.dict())
        req_body = req_vo.ExportConverter(PRJ_ID=client_info.project,
                                          CNVRT_NM=self.__name,
                                          CNVRT_IN=CNVRT_IN,
                                          CNVRT_OUT=CNVRT_OUT,
                                          DESC=self.__description,
                                          CNVRT_BCKN=self.__backend,
                                          CNVRT_RVSN_DESC=description,
                                          CNVRT_PKG=self.__requirements,
                                          REG_ID=client_info.user,
                                          CNVRT_NMSPC=self.__namespace,
                                          CNVRT_SCRIPT=self.__script)
        code, msg = req_util.post(url=url, data=req_body.dict())
        if code != 0:
            raise RuntimeError(f"failed to export converter. {msg}")
        else:
            print(f"export success.")

    def __validate_args(self):
        validate_converter_script(self.__script)
        if not isinstance( self.__input_signature, list):
            raise TypeError(f"unsupported i/o signature {self.__input_signature}. use IO class in xflow.deploy")
        else:
            for _ in self.__input_signature:
                if not isinstance(_, IOSignature):
                    raise TypeError(f"unsupported i/o signature {self.__input_signature}. use IO class in xflow.deploy")
        if not isinstance( self.__output_signature, list):
            raise TypeError(f"unsupported i/o signature {self.__output_signature}. use IO class in xflow.deploy")
        else:
            for _ in self.__output_signature:
                if not isinstance(_, IOSignature):
                    raise TypeError(f"unsupported i/o signature {self.__output_signature}. use IO class in xflow.deploy")

    @property
    def name(self):
        return self.__name

    @property
    def script(self):
        return self.__script

    @property
    def input_signature(self):
        return self.__input_signature

    @property
    def output_signature(self):
        return self.__output_signature

    @property
    def requirements(self):
        return self.__requirements

    @property
    def namespace(self):
        return self.__namespace

    @property
    def backend(self):
        return self.__backend

    @property
    def description(self):
        return self.__description


