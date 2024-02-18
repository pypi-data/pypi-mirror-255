from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SidecarLink(_message.Message):
    __slots__ = ("id", "sidecar_id", "datastore_id", "port", "datastore_name", "termination_protection")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIDECAR_ID_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_ID_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    sidecar_id: str
    datastore_id: str
    port: int
    datastore_name: str
    termination_protection: bool
    def __init__(self, id: _Optional[str] = ..., sidecar_id: _Optional[str] = ..., datastore_id: _Optional[str] = ..., port: _Optional[int] = ..., datastore_name: _Optional[str] = ..., termination_protection: bool = ...) -> None: ...
