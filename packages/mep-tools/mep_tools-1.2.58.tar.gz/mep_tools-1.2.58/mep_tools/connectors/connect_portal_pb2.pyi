from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ATS: _ClassVar[TypeEnum]
    CHANNEL: _ClassVar[TypeEnum]
    INTEGRATION: _ClassVar[TypeEnum]

class OperationEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    GET: _ClassVar[OperationEnum]
    CREATE: _ClassVar[OperationEnum]
    READ: _ClassVar[OperationEnum]
    UPDATE: _ClassVar[OperationEnum]
    DELETE: _ClassVar[OperationEnum]
    SYNC: _ClassVar[OperationEnum]
    AUTHENTICATE: _ClassVar[OperationEnum]
ATS: TypeEnum
CHANNEL: TypeEnum
INTEGRATION: TypeEnum
GET: OperationEnum
CREATE: OperationEnum
READ: OperationEnum
UPDATE: OperationEnum
DELETE: OperationEnum
SYNC: OperationEnum
AUTHENTICATE: OperationEnum

class PortalGetRequest(_message.Message):
    __slots__ = ["portal_uuid"]
    PORTAL_UUID_FIELD_NUMBER: _ClassVar[int]
    portal_uuid: str
    def __init__(self, portal_uuid: _Optional[str] = ...) -> None: ...

class PortalReadRequest(_message.Message):
    __slots__ = ["company_uuid"]
    COMPANY_UUID_FIELD_NUMBER: _ClassVar[int]
    company_uuid: str
    def __init__(self, company_uuid: _Optional[str] = ...) -> None: ...

class PortalDeleteRequest(_message.Message):
    __slots__ = ["portal_uuid"]
    PORTAL_UUID_FIELD_NUMBER: _ClassVar[int]
    portal_uuid: str
    def __init__(self, portal_uuid: _Optional[str] = ...) -> None: ...

class PortalMetricRequest(_message.Message):
    __slots__ = ["portal_uuid"]
    PORTAL_UUID_FIELD_NUMBER: _ClassVar[int]
    portal_uuid: str
    def __init__(self, portal_uuid: _Optional[str] = ...) -> None: ...

class PortalCreateRequest(_message.Message):
    __slots__ = ["company_uuid", "name", "type", "className", "configuration"]
    COMPANY_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CLASSNAME_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    company_uuid: str
    name: str
    type: TypeEnum
    className: str
    configuration: _any_pb2.Any
    def __init__(self, company_uuid: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[TypeEnum, str]] = ..., className: _Optional[str] = ..., configuration: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class PortalUpdateRequest(_message.Message):
    __slots__ = ["portal_uuid", "name", "configuration"]
    PORTAL_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    portal_uuid: str
    name: str
    configuration: _any_pb2.Any
    def __init__(self, portal_uuid: _Optional[str] = ..., name: _Optional[str] = ..., configuration: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class PortalResponse(_message.Message):
    __slots__ = ["operation", "success", "uuid", "name", "type", "key", "className", "configuration", "created_at", "updated_at"]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    CLASSNAME_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    operation: OperationEnum
    success: bool
    uuid: str
    name: str
    type: TypeEnum
    key: str
    className: str
    configuration: _any_pb2.Any
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, operation: _Optional[_Union[OperationEnum, str]] = ..., success: bool = ..., uuid: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[TypeEnum, str]] = ..., key: _Optional[str] = ..., className: _Optional[str] = ..., configuration: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PortalsResponse(_message.Message):
    __slots__ = ["operation", "success", "portals"]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PORTALS_FIELD_NUMBER: _ClassVar[int]
    operation: OperationEnum
    success: bool
    portals: _containers.RepeatedCompositeFieldContainer[PortalResponse]
    def __init__(self, operation: _Optional[_Union[OperationEnum, str]] = ..., success: bool = ..., portals: _Optional[_Iterable[_Union[PortalResponse, _Mapping]]] = ...) -> None: ...
