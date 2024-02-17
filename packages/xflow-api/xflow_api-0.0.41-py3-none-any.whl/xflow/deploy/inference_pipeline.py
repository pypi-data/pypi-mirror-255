from typing import Optional

from xflow._utils.decorators import client_method
from xflow.deploy.types import IOSignature
import xflow._private.client as xflow_client
from xflow.deploy._util import validate_converter
from xflow._utils.converter import Converter


@client_method
def create_converter(name: str, script_file: str, input_signature: list[IOSignature],
                     output_signature: list[IOSignature], requirements_file: Optional[str] = None,
                     description: Optional[str] = '', namespace: Optional[str] = "default",
                     backend: Optional[str] = "python3.11") -> Converter:
    validate_converter(script_file)
    xflow_client.init_check()
    package_list = []
    if requirements_file is not None:
        with open(requirements_file, 'r') as requirements:
            lines = requirements.readlines()
            for line in lines:
                package_list.append(line.strip())
    with open(script_file, 'r') as script_f:
        script = script_f.read()
    return Converter(name=name, script=script, input_signature=input_signature, output_signature=output_signature,
                     namespace=namespace, backend=backend, requirements=package_list, description=description)
