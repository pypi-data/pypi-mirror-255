from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RunnerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RunnerBase: _ClassVar[RunnerType]
    RunnerGo: _ClassVar[RunnerType]
    RunnerLocal: _ClassVar[RunnerType]
RunnerBase: RunnerType
RunnerGo: RunnerType
RunnerLocal: RunnerType

class Ping(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Hello(_message.Message):
    __slots__ = ("spec",)
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: AgentSpec
    def __init__(self, spec: _Optional[_Union[AgentSpec, _Mapping]] = ...) -> None: ...

class Goodbye(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatusUpdate(_message.Message):
    __slots__ = ("state", "message")
    class AgentState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Unknown: _ClassVar[StatusUpdate.AgentState]
        OK: _ClassVar[StatusUpdate.AgentState]
        Requested: _ClassVar[StatusUpdate.AgentState]
        AwaitingPromise: _ClassVar[StatusUpdate.AgentState]
        Working: _ClassVar[StatusUpdate.AgentState]
        Missing: _ClassVar[StatusUpdate.AgentState]
        Error: _ClassVar[StatusUpdate.AgentState]
        Completed: _ClassVar[StatusUpdate.AgentState]
    Unknown: StatusUpdate.AgentState
    OK: StatusUpdate.AgentState
    Requested: StatusUpdate.AgentState
    AwaitingPromise: StatusUpdate.AgentState
    Working: StatusUpdate.AgentState
    Missing: StatusUpdate.AgentState
    Error: StatusUpdate.AgentState
    Completed: StatusUpdate.AgentState
    STATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    state: StatusUpdate.AgentState
    message: str
    def __init__(self, state: _Optional[_Union[StatusUpdate.AgentState, str]] = ..., message: _Optional[str] = ...) -> None: ...

class Promise(_message.Message):
    __slots__ = ("name", "type", "source", "state", "data", "link")
    class PromiseState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Pending: _ClassVar[Promise.PromiseState]
        Fulfilled: _ClassVar[Promise.PromiseState]
        Final: _ClassVar[Promise.PromiseState]
        Empty: _ClassVar[Promise.PromiseState]
    Pending: Promise.PromiseState
    Fulfilled: Promise.PromiseState
    Final: Promise.PromiseState
    Empty: Promise.PromiseState
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    source: str
    state: Promise.PromiseState
    data: bytes
    link: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., source: _Optional[str] = ..., state: _Optional[_Union[Promise.PromiseState, str]] = ..., data: _Optional[bytes] = ..., link: _Optional[str] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ("type", "promise")
    class ResultType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Result: _ClassVar[Result.ResultType]
        PartialResult: _ClassVar[Result.ResultType]
        NoResult: _ClassVar[Result.ResultType]
    Result: Result.ResultType
    PartialResult: Result.ResultType
    NoResult: Result.ResultType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROMISE_FIELD_NUMBER: _ClassVar[int]
    type: Result.ResultType
    promise: Promise
    def __init__(self, type: _Optional[_Union[Result.ResultType, str]] = ..., promise: _Optional[_Union[Promise, _Mapping]] = ...) -> None: ...

class Log(_message.Message):
    __slots__ = ("severity", "message")
    class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Debug: _ClassVar[Log.Severity]
        Info: _ClassVar[Log.Severity]
        Warning: _ClassVar[Log.Severity]
        Error: _ClassVar[Log.Severity]
        Critical: _ClassVar[Log.Severity]
    Debug: Log.Severity
    Info: Log.Severity
    Warning: Log.Severity
    Error: Log.Severity
    Critical: Log.Severity
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    severity: Log.Severity
    message: str
    def __init__(self, severity: _Optional[_Union[Log.Severity, str]] = ..., message: _Optional[str] = ...) -> None: ...

class Halt(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HaltAndCatchFire(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Message(_message.Message):
    __slots__ = ("id", "index", "source", "priority", "timeSent", "timeRecv", "ping", "hello", "goodbye", "statusUpdate", "result", "log", "halt", "haltAndCatchFire", "createAgent")
    ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    TIMESENT_FIELD_NUMBER: _ClassVar[int]
    TIMERECV_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    HELLO_FIELD_NUMBER: _ClassVar[int]
    GOODBYE_FIELD_NUMBER: _ClassVar[int]
    STATUSUPDATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    HALT_FIELD_NUMBER: _ClassVar[int]
    HALTANDCATCHFIRE_FIELD_NUMBER: _ClassVar[int]
    CREATEAGENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    index: int
    source: str
    priority: int
    timeSent: _timestamp_pb2.Timestamp
    timeRecv: _timestamp_pb2.Timestamp
    ping: Ping
    hello: Hello
    goodbye: Goodbye
    statusUpdate: StatusUpdate
    result: Result
    log: Log
    halt: Halt
    haltAndCatchFire: HaltAndCatchFire
    createAgent: AgentSpec
    def __init__(self, id: _Optional[int] = ..., index: _Optional[int] = ..., source: _Optional[str] = ..., priority: _Optional[int] = ..., timeSent: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., timeRecv: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ping: _Optional[_Union[Ping, _Mapping]] = ..., hello: _Optional[_Union[Hello, _Mapping]] = ..., goodbye: _Optional[_Union[Goodbye, _Mapping]] = ..., statusUpdate: _Optional[_Union[StatusUpdate, _Mapping]] = ..., result: _Optional[_Union[Result, _Mapping]] = ..., log: _Optional[_Union[Log, _Mapping]] = ..., halt: _Optional[_Union[Halt, _Mapping]] = ..., haltAndCatchFire: _Optional[_Union[HaltAndCatchFire, _Mapping]] = ..., createAgent: _Optional[_Union[AgentSpec, _Mapping]] = ...) -> None: ...

class AgentSpec(_message.Message):
    __slots__ = ("name", "runner", "runnerType", "pollInterval_ms", "pingInterval_ms", "allowedPollRetries", "allowedPingRetries", "entrypoint", "blackboards", "attributes")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    RUNNER_FIELD_NUMBER: _ClassVar[int]
    RUNNERTYPE_FIELD_NUMBER: _ClassVar[int]
    POLLINTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    PINGINTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    ALLOWEDPOLLRETRIES_FIELD_NUMBER: _ClassVar[int]
    ALLOWEDPINGRETRIES_FIELD_NUMBER: _ClassVar[int]
    ENTRYPOINT_FIELD_NUMBER: _ClassVar[int]
    BLACKBOARDS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    runner: str
    runnerType: RunnerType
    pollInterval_ms: int
    pingInterval_ms: int
    allowedPollRetries: int
    allowedPingRetries: int
    entrypoint: str
    blackboards: _containers.RepeatedScalarFieldContainer[str]
    attributes: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., runner: _Optional[str] = ..., runnerType: _Optional[_Union[RunnerType, str]] = ..., pollInterval_ms: _Optional[int] = ..., pingInterval_ms: _Optional[int] = ..., allowedPollRetries: _Optional[int] = ..., allowedPingRetries: _Optional[int] = ..., entrypoint: _Optional[str] = ..., blackboards: _Optional[_Iterable[str]] = ..., attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CreateAgent(_message.Message):
    __slots__ = ("agentSpec",)
    AGENTSPEC_FIELD_NUMBER: _ClassVar[int]
    agentSpec: AgentSpec
    def __init__(self, agentSpec: _Optional[_Union[AgentSpec, _Mapping]] = ...) -> None: ...

class GetMessagesRequest(_message.Message):
    __slots__ = ("startingAt", "filterPings")
    STARTINGAT_FIELD_NUMBER: _ClassVar[int]
    FILTERPINGS_FIELD_NUMBER: _ClassVar[int]
    startingAt: int
    filterPings: bool
    def __init__(self, startingAt: _Optional[int] = ..., filterPings: bool = ...) -> None: ...

class MessageStack(_message.Message):
    __slots__ = ("messages",)
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[Message]
    def __init__(self, messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ...) -> None: ...

class Ack(_message.Message):
    __slots__ = ("status", "message")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[Ack.Status]
    OK: Ack.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: Ack.Status
    message: str
    def __init__(self, status: _Optional[_Union[Ack.Status, str]] = ..., message: _Optional[str] = ...) -> None: ...

class FileDownload(_message.Message):
    __slots__ = ("Name", "IsDir", "URL", "Checksum")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ISDIR_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    Name: str
    IsDir: bool
    URL: str
    Checksum: str
    def __init__(self, Name: _Optional[str] = ..., IsDir: bool = ..., URL: _Optional[str] = ..., Checksum: _Optional[str] = ...) -> None: ...
