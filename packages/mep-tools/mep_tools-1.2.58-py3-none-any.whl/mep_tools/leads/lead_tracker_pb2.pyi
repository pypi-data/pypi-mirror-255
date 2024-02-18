from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class NewLeadRequest(_message.Message):
    __slots__ = ["payload"]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    payload: str
    def __init__(self, payload: _Optional[str] = ...) -> None: ...

class NewLeadResponse(_message.Message):
    __slots__ = ["payload"]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    payload: str
    def __init__(self, payload: _Optional[str] = ...) -> None: ...
