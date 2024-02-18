from .types.v1 import satellite_pb2 as _satellite_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateSatelliteRequest(_message.Message):
    __slots__ = ("name", "termination_protection")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    termination_protection: bool
    def __init__(self, name: _Optional[str] = ..., termination_protection: bool = ...) -> None: ...

class CreateSatelliteResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetSatelliteByIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetSatelliteByIdResponse(_message.Message):
    __slots__ = ("satellite",)
    SATELLITE_FIELD_NUMBER: _ClassVar[int]
    satellite: _satellite_pb2.Satellite
    def __init__(self, satellite: _Optional[_Union[_satellite_pb2.Satellite, _Mapping]] = ...) -> None: ...

class GetSatellitesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetSatellitesResponse(_message.Message):
    __slots__ = ("satellites",)
    SATELLITES_FIELD_NUMBER: _ClassVar[int]
    satellites: _containers.RepeatedCompositeFieldContainer[_satellite_pb2.Satellite]
    def __init__(self, satellites: _Optional[_Iterable[_Union[_satellite_pb2.Satellite, _Mapping]]] = ...) -> None: ...

class GetSatelliteApiKeyRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetSatelliteApiKeyResponse(_message.Message):
    __slots__ = ("api_key",)
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    def __init__(self, api_key: _Optional[str] = ...) -> None: ...

class UpdateSatelliteRequest(_message.Message):
    __slots__ = ("id", "name", "termination_protection")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    termination_protection: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., termination_protection: bool = ...) -> None: ...

class UpdateSatelliteResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteSatelliteRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteSatelliteResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SatelliteOnlineInstance(_message.Message):
    __slots__ = ("instance_id", "last_seen", "start_time", "version")
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    instance_id: str
    last_seen: _timestamp_pb2.Timestamp
    start_time: _timestamp_pb2.Timestamp
    version: str
    def __init__(self, instance_id: _Optional[str] = ..., last_seen: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., version: _Optional[str] = ...) -> None: ...

class GetOnlineInstancesBySatelliteIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetOnlineInstancesBySatelliteIdResponse(_message.Message):
    __slots__ = ("instances",)
    INSTANCES_FIELD_NUMBER: _ClassVar[int]
    instances: _containers.RepeatedCompositeFieldContainer[SatelliteOnlineInstance]
    def __init__(self, instances: _Optional[_Iterable[_Union[SatelliteOnlineInstance, _Mapping]]] = ...) -> None: ...
