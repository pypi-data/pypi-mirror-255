from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Satellite(_message.Message):
    __slots__ = ("id", "name", "status", "termination_protection")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    status: str
    termination_protection: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., status: _Optional[str] = ..., termination_protection: bool = ...) -> None: ...
