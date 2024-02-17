from dataclasses import dataclass


@dataclass
class ModelTypes:
    TensorRT: str = "TENSOR_RT"
    TensorFlow: str = "TENSORFLOW"
    PyTorch: str = "PYTORCH"
    ONNX: str = "ONNX"
    Python: str = "PYTHON"

