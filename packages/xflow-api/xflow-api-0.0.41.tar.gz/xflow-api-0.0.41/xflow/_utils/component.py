import inspect
import types
from types import GenericAlias
import typing
from dataclasses import dataclass

from xflow._private.request_vo import ExportComponent
import xflow._private.client as xflow_client
from xflow._private._constants import RequestPath
import xflow._utils.request_util as req_util


@dataclass
class ComponentTypeCode:
    DATA: str = '1'
    EXPERIMENT: str = '2'


COMPONENT_TYPE_CODE = ComponentTypeCode()


class Component:
    def __init__(self, name: str, func: callable, component_type: str, namespace: str = 'default',
                 script: str | None = None, desc: str = '', output_names: list[str] | None = None):
        self.__name: str = name[:100]
        self.__func: callable = func
        self.__description: str = desc[:4000]
        self.__namespace: str = namespace
        self.__updated: bool = True
        self.__output_names: list[str] | None = output_names
        if component_type not in COMPONENT_TYPE_CODE.__dict__.values():
            raise AttributeError("undefined component type")
        self.__component_type: str = component_type
        self.__args: dict = get_io_info(func, output_names)
        if script is None:
            self.__script: str = get_script(func)
            if len(self.__script) > 16777215:
                raise ValueError("script is too long to export. maximum size of 16,777,215 character")
        else:
            self.__script: str = script
        # self.__func_obj: bytes = pickled_func(func)

    def __call__(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

    def execute(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

    def commit(self, commit_message: str):
        if self.__updated:
            xflow_client.init_check()
            script = self.__script.replace("\r", "\\r")
            client_info: xflow_client.ClientInformation = xflow_client.client_info
            url = client_info.xflow_server_url + RequestPath.pipeline_export_component
            body = ExportComponent(REG_ID=client_info.user,
                                   PRJ_ID=client_info.project,
                                   CMPNT_NM=self.__name,
                                   CMPNT_TYPE_CD=self.__component_type,
                                   CMPNT_FUNC_NM=self.__func.__name__,
                                   CMPNT_NMSPC=self.__namespace,
                                   CMPNT_RVSN_DESC=commit_message,
                                   CMPNT_IN={"inputs": self.__args["inputs"]},
                                   CMPNT_OUT={"outputs": self.__args["outputs"]},
                                   CMPNT_SCRIPT=script,
                                   CMPNT_DESC=self.__description)
            # func_obj = {"file": io.BytesIO(self.__func_obj)}

            code, msg = req_util.post(url=url, data=body.dict())
            if code == 0:
                self.__updated = False
                print(f"committed. revision: {msg['REV']}")
            else:
                print(f"commit failed: {msg['ERROR_MSG']}")
        else:
            print("No changes, commit has no effect")

    def update(self, func: callable, output_names: list[str] | None = None):
        new_script = get_script(func)
        if len(new_script) > 16777215:
            raise ValueError("script is too long to export. maximum size of 16,777,215 character")
        if self.__script == new_script:
            print("No changes, update has no effect")
        else:
            self.__script = new_script
            self.__func = func
            self.__args = get_io_info(func, output_names)
            # self.__func_obj = pickled_func(func)
            self.__updated = True
            print("Update success")

    @property
    def args(self):
        return self.__args

    @property
    def name(self):
        return self.__name

    @property
    def script(self):
        return self.__script

    @property
    def description(self):
        return self.__description

    # @property
    # def func_obj(self):
    #     return self.__func_obj

    @property
    def component_type(self):
        return self.__component_type

    @property
    def namespace(self):
        return self.__namespace

    @property
    def output_names(self):
        return self.__output_names


# class Capturing(list):
#     def __enter__(self):
#         self._stdout = sys.stdout
#         sys.stdout = self._stringio = StringIO()
#         return self
#
#     def __exit__(self, *args):
#         self.extend(self._stringio.getvalue().splitlines())
#         del self._stringio
#         sys.stdout = self._stdout


def get_io_info(func: callable, output_names: list[str] | None = None) -> dict[str, dict | list]:
    inputs = {}
    outputs = []
    full_spec = inspect.getfullargspec(func)
    args = full_spec.args
    args_info = full_spec.annotations
    t_input_info = args_info.copy()
    if "return" in t_input_info:
        del t_input_info["return"]
    for arg in args:
        if arg not in t_input_info:
            raise AttributeError(f"type must be specified for component. use type hint for: {arg}")
    if "return" in args_info:
        output_info = args_info["return"]
        del args_info["return"]
        if output_info is not None:
            if output_info.__name__ == tuple.__name__:
                if isinstance(output_info, GenericAlias):
                    for arg in output_info.__args__:
                        outputs.append(arg.__name__)
            else:
                outputs.append(output_info.__name__)
    for arg, type_ in args_info.items():
        if isinstance(type_, typing._SpecialForm):
            raise AttributeError(f"The type must be specified for Optional. e.g Optional[int]. use type hint for: {arg}")
        if isinstance(type_, types.UnionType):
            raise AttributeError(f"union type is not permitted on component. use type hint for: {arg}")
        if isinstance(type_, typing._UnionGenericAlias):
            if len(type_.__args__) > 2:
                raise AttributeError(f"union type is not permitted on component. use type hint for: {arg}")
            has_None = False
            for T in type_.__args__:
                if T.__name__ != "NoneType":
                    inputs[arg] = type_.__name__ + '[' + T.__name__ + ']'
                else:
                    has_None = True
            if not has_None:
                raise AttributeError(f"union type is not permitted on component. use type hint for: {arg}")
        else:
            inputs[arg] = type_.__name__
    io_info = {"inputs": inputs, "outputs": outputs}
    if output_names is not None:
        if len(output_names) != len(list(dict.fromkeys(output_names).keys())):
            raise AttributeError("output_names has duplicated value")
        if not isinstance(output_names, list):
            raise AttributeError("type of output_name is not list")
        if len(output_names) != len(io_info["outputs"]):
            raise AttributeError("length of output_name is not matched with outputs")
        outputs = []
        for _ in range(len(output_names)):
            if not isinstance(output_names[_], str):
                raise TypeError("output_names must be string")
            outputs.append({output_names[_]: io_info["outputs"][_]})
        io_info["outputs"] = outputs
    return io_info


def get_script(func: callable) -> str:
    func_string = inspect.getsource(func)
    return func_string
    # ipython = get_ipython()
    # if ipython:
    #     with Capturing() as output:
    #         ipython.run_line_magic("pinfo2", func.__name__)
    #     s_idx = -1
    #     e_idx = -1
    #     for idx, line in enumerate(output):
    #         if "Source" in line:
    #             s_idx = idx + 1
    #         elif "File" in line or "Type" in line:
    #             e_idx = idx - 1
    #     if s_idx != -1 and e_idx != -1:
    #         func_string = '\n'.join(output[s_idx:e_idx])
    #         return func_string
    #     else:
    #         raise SyntaxError("\n".join(output))
    # else:
    #     func_string = inspect.getsource(func)
    #     return func_string


# def pickled_func(func: callable) -> bytes:
#     return dill.dumps(func)
#     # return cloudpickle.dumps(func)
#
#
# def restore_func(func_obj: bytes) -> callable:
#     return dill.loads(func_obj)
