import inspect


def handler(base_url: str):
    caller_frame = inspect.currentframe().f_back.f_locals
    caller_args = caller_frame.f_locals
    print(base_url.format(**caller_args))


def caller(region, tier, division):
    return handler(base_url="http://127.0.0.1:5000/{region}/{tier}/{division}")



caller("euw1", "GOLD", "I")