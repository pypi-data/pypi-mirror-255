from .types.v1 import list_metadata_pb2 as _list_metadata_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from ...validate.v1 import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListIntegrationMfasRequest(_message.Message):
    __slots__ = ("limit", "cursor", "order")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    limit: int
    cursor: str
    order: str
    def __init__(self, limit: _Optional[int] = ..., cursor: _Optional[str] = ..., order: _Optional[str] = ...) -> None: ...

class ListIntegrationMfasResponse(_message.Message):
    __slots__ = ("integrations", "list_metadata")
    INTEGRATIONS_FIELD_NUMBER: _ClassVar[int]
    LIST_METADATA_FIELD_NUMBER: _ClassVar[int]
    integrations: _containers.RepeatedCompositeFieldContainer[IntegrationMfa]
    list_metadata: _list_metadata_pb2.ListMetadata
    def __init__(self, integrations: _Optional[_Iterable[_Union[IntegrationMfa, _Mapping]]] = ..., list_metadata: _Optional[_Union[_list_metadata_pb2.ListMetadata, _Mapping]] = ...) -> None: ...

class GetIntegrationMfaByIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetIntegrationMfaByIdResponse(_message.Message):
    __slots__ = ("integration",)
    INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    integration: IntegrationMfa
    def __init__(self, integration: _Optional[_Union[IntegrationMfa, _Mapping]] = ...) -> None: ...

class CreateIntegrationMfaRequest(_message.Message):
    __slots__ = ("type", "duo_integration_key", "duo_secret_key", "duo_api_hostname", "termination_protection")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DUO_INTEGRATION_KEY_FIELD_NUMBER: _ClassVar[int]
    DUO_SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    DUO_API_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    type: str
    duo_integration_key: str
    duo_secret_key: str
    duo_api_hostname: str
    termination_protection: bool
    def __init__(self, type: _Optional[str] = ..., duo_integration_key: _Optional[str] = ..., duo_secret_key: _Optional[str] = ..., duo_api_hostname: _Optional[str] = ..., termination_protection: bool = ...) -> None: ...

class CreateIntegrationMfaResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteIntegrationMfaRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteIntegrationMfaResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateIntegrationMfaRequest(_message.Message):
    __slots__ = ("id", "termination_protection")
    ID_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    termination_protection: bool
    def __init__(self, id: _Optional[str] = ..., termination_protection: bool = ...) -> None: ...

class UpdateIntegrationMfaResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IntegrationMfa(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "type", "duo_integration_key", "duo_secret_key", "duo_api_hostname", "termination_protection")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DUO_INTEGRATION_KEY_FIELD_NUMBER: _ClassVar[int]
    DUO_SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    DUO_API_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    type: str
    duo_integration_key: str
    duo_secret_key: str
    duo_api_hostname: str
    termination_protection: bool
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[str] = ..., duo_integration_key: _Optional[str] = ..., duo_secret_key: _Optional[str] = ..., duo_api_hostname: _Optional[str] = ..., termination_protection: bool = ...) -> None: ...
