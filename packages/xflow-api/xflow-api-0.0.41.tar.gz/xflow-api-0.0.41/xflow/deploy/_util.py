import importlib.abc, importlib.util
import inspect
from types import ModuleType
import sys


def validate_converter(path: str):
    triton_util = ModuleType('triton_python_backend_utils')
    sys.modules['triton_python_backend_utils'] = triton_util
    spec = importlib.util.spec_from_file_location("converter", location=path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for _ in inspect.getmembers(module):
        if "TritonPythonModel" in _:
            if hasattr(module.TritonPythonModel, "execute"):
                return
    else:
        raise AttributeError("convert function must be defined in converter script")


class StringLoader(importlib.abc.SourceLoader):
    def __init__(self, data):
        self.data = data

    def get_source(self, fullname):
        return self.data

    def get_data(self, path):
        return self.data.encode("utf-8")

    def get_filename(self, fullname):
        return "<not a real path>/" + fullname + ".py"


def validate_converter_script(script: str):
    triton_util = ModuleType('triton_python_backend_utils')
    sys.modules['triton_python_backend_utils'] = triton_util
    loader = StringLoader(script)
    spec = importlib.util.spec_from_loader("converter", loader, origin="built-in")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for _ in inspect.getmembers(module):
        if "TritonPythonModel" in _:
            if hasattr(module.TritonPythonModel, "execute"):
                return
    else:
        raise AttributeError("convert function must be defined in converter script")

