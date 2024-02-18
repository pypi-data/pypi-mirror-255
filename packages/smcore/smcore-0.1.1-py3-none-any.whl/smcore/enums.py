# These are just aliases to make an agent implementation a little
# easier.  Only acceptable because the we should only ever need
# to update if we remove or add states.  My HOPE is that it's not
# necessary beyond the occasional tweak.

from . import types_pb2 as pb2
from enum import IntEnum

class Log(IntEnum):
    DEBUG = pb2.Log.Severity.Debug
    INFO = pb2.Log.Severity.Info
    WARNING = pb2.Log.Severity.Warning
    ERROR = pb2.Log.Severity.Error
    CRITICAL = pb2.Log.Severity.Critical

class AgentState(IntEnum):
    UNKNOWN = pb2.StatusUpdate.AgentState.Unknown
    OK = pb2.StatusUpdate.AgentState.OK
    REQUESTED = pb2.StatusUpdate.AgentState.Requested
    AWAITING_PROMISE = pb2.StatusUpdate.AgentState.AwaitingPromise
    WORKING  = pb2.StatusUpdate.AgentState.Working
    MISSING = pb2.StatusUpdate.AgentState.Missing
    ERROR = pb2.StatusUpdate.AgentState.Error
    COMPLETED = pb2.StatusUpdate.AgentState.Completed

class ResultType(IntEnum):
    RESULT = pb2.Result.ResultType.Result
    PARTIAL_RESULT = pb2.Result.ResultType.PartialResult
    NO_RESULT = pb2.Result.ResultType.NoResult

class PromiseState(IntEnum):
    PENDING = pb2.Promise.PromiseState.Pending
    FULFILLED  = pb2.Promise.PromiseState.Fulfilled
    FINAL = pb2.Promise.PromiseState.Final
    EMPTY = pb2.Promise.PromiseState.Empty
