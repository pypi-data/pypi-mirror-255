import functools

from xflow._private._constants import RuntimeEnvType, RUNTIME_ENV


def client_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if RUNTIME_ENV != RuntimeEnvType.CLIENT:
            raise RuntimeError(f"client method '{func.__name__}' can't be executed on executor side")
        return func(*args, **kwargs)
    return wrapper


def executor_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if RUNTIME_ENV != RuntimeEnvType.EXECUTOR:
            print(f"warning: '{func.__name__}' method only runs on the executor side. skipping")
            return
        return func(*args, **kwargs)
    return wrapper
