from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OperationEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    GET: _ClassVar[OperationEnum]
    CREATE: _ClassVar[OperationEnum]
    READ: _ClassVar[OperationEnum]
    UPDATE: _ClassVar[OperationEnum]
    DELETE: _ClassVar[OperationEnum]
GET: OperationEnum
CREATE: OperationEnum
READ: OperationEnum
UPDATE: OperationEnum
DELETE: OperationEnum

class ChartDispatcherGetRequest(_message.Message):
    __slots__ = ["chart_uuid"]
    CHART_UUID_FIELD_NUMBER: _ClassVar[int]
    chart_uuid: str
    def __init__(self, chart_uuid: _Optional[str] = ...) -> None: ...

class ChartDispatcherCreateRequest(_message.Message):
    __slots__ = ["chart_uuid", "dispatcher"]
    CHART_UUID_FIELD_NUMBER: _ClassVar[int]
    DISPATCHER_FIELD_NUMBER: _ClassVar[int]
    chart_uuid: str
    dispatcher: _any_pb2.Any
    def __init__(self, chart_uuid: _Optional[str] = ..., dispatcher: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ChartDispatcherUpdateRequest(_message.Message):
    __slots__ = ["chart_uuid", "dispatcher"]
    CHART_UUID_FIELD_NUMBER: _ClassVar[int]
    DISPATCHER_FIELD_NUMBER: _ClassVar[int]
    chart_uuid: str
    dispatcher: _any_pb2.Any
    def __init__(self, chart_uuid: _Optional[str] = ..., dispatcher: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ChartDispatcherDeleteRequest(_message.Message):
    __slots__ = ["chart_uuid"]
    CHART_UUID_FIELD_NUMBER: _ClassVar[int]
    chart_uuid: str
    def __init__(self, chart_uuid: _Optional[str] = ...) -> None: ...

class ChartDispatcherResponse(_message.Message):
    __slots__ = ["operation", "success", "chart_uuid", "dispatcher", "created_at", "updated_at"]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CHART_UUID_FIELD_NUMBER: _ClassVar[int]
    DISPATCHER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    operation: OperationEnum
    success: bool
    chart_uuid: str
    dispatcher: _any_pb2.Any
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, operation: _Optional[_Union[OperationEnum, str]] = ..., success: bool = ..., chart_uuid: _Optional[str] = ..., dispatcher: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
