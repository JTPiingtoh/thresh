from typing import Literal



Count = int
Limit = int
WindowExpire = float
Latency = float
Pinged = float

Scope = Literal['app', 'method']
Id = int
Region = str

Target = tuple[Scope, Id, Region]
TargetState = tuple[Count, Limit, WindowExpire, Latency, Pinged]