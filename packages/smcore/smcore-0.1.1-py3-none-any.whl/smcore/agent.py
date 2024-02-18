import sys
import re
import datetime
import json
from threading import Lock
import asyncio
import time
import traceback

import argparse
#from .promise_set import PromiseSet, parse_promise
#from .promise_set import PromiseSet, parse_promise
from .attributes import Attributes

from .enums import AgentState
from . import types_pb2 as pb2
import google.protobuf.json_format as json_format
from google.protobuf.timestamp_pb2 import Timestamp

#from blackboard_grpc_client import BlackboardGRPCClient
#client_type = BlackboardGRPCClient

from .blackboard_http_client import BlackboardHTTPClient
client_type = BlackboardHTTPClient

# ----------------------------------------
# Agent base class
# Inheritors must implement self.run()
# ----------------------------------------
class Agent(client_type):

    bb_client = None

    is_fullfilled = asyncio.Event()
    blackboard_remote_addr = ""
    last_msg_idx = 0
    stopped = False
    mutex = Lock()
    promises = None
    start_time = time.monotonic()
    attributes = None
    
    def __init__(self, spec, bb_addr):
        self.spec = spec
        super().__init__(bb_addr)
        self.blackboard_remote_addr = bb_addr
        self.attributes = Attributes(self.spec.attributes)
        
    # Primary AgentHTTP interface that users should employ when writing
    # their own agents
    def log(self, severity, message, stdout=True):
        log_message = pb2.Message(log=pb2.Log(severity=severity, message = message))
        self.send_message(log_message)
        if stdout:
            monotonic_time = time.monotonic() - self.start_time
            monotonic_time = int(round(monotonic_time, 0)) #make it nicer to print
            print("%05d %-10s %s" % (monotonic_time, str(severity).removeprefix("Log."), message))
        
    def post_status_update(self, state, message):
        #status_update = {"state": str(state), "message": update}
        status_update = pb2.Message(statusUpdate=pb2.StatusUpdate(state=state, message=message))
        self.send_message(status_update)
        
    def post_result(self, res_name: str, res_type: str, data: dict):
        # Convert the data dictionary to json
        json_data = json.dumps(data)
        
        promise = pb2.Promise(
            name=res_name,
            type=res_type,
            state=pb2.Promise.PromiseState.Final,
            data=json_data.encode("utf-8"),
            source=self.spec.name,
        )

        result = pb2.Result(
            type=pb2.Result.ResultType.Result,
            promise=promise,
        )

        msg = pb2.Message(result=result)
        
        self.send_message(msg)
        
    def post_partial_result(self, res_name: str, res_type: str, data: dict):
        json_data = json.dumps(data)
        
        promise = pb2.Promise(
            name=res_name,
            type=res_type,
            state=pb2.Promise.PromiseState.Fulfilled,
            data=json_data.encode("utf-8"),
            source=self.spec.name,
        )

        result = pb2.Result(
            type=pb2.Result.ResultType.PartialResult,
            promise=promise,
        )
        
        msg = pb2.Message(result=result)
        
        self.send_message(msg)

    def post_no_result(self, res_name: str, res_type: str, data: dict):
        json_data = json.dumps(data)

        promise = pb2.Promise(
            name=res_name,
            type=res_type,
            state=pb2.Promise.PromiseState.Empty,
            data=json_data.encode("utf-8"),
            source=self.spec.name,
        )

        result = pb2.Result(
            type=pb2.Result.ResultType.NoResult,
            promise=promise,
        )
        
        msg = pb2.Message(result=result)
        
        self.send_message(msg)
        
    # Users should not generally need to call these methods directly, as
    # they are handled by the base class, however they are available if needed
    def send_ping(self):
        self.send_message(pb2.Message(ping={}))

    def say_hello(self):
        msg = pb2.Message(hello={})
        self.send_message(msg)

    def say_goodbye(self):
        msg = pb2.Message(goodbye={})
        self.send_message(msg)

    # send_messages sends a message to the configured blackboard (via the HTTP
    # interface).  In general, users should try  to prefer the higher-level methods
    # (such as post_status_update, log, post_result, etc.)
    #
    # msg_type should be one of those specified in message_types.py
    # data should be the marshaled JSON string (not bytes) of your message content
    # send_message is inherited from the Blackboard*Client (), hence the _ prefix
    # We also want to discourage folks from using the _send_message method directly
    # as this is not really our intended interface. It should only be used in advanced
    # use cases that are not currently supported by SM.
    def send_message(self, msg):
        msg.source = self.spec.name
        msg.timeSent.GetCurrentTime()
        self._send_message(msg)
        
    async def start(self):
        self.say_hello()
        await asyncio.gather(
            self._ping_loop(),
            self._message_thread(),
            self.run(),
        )

    def launch(self):
        asyncio.run(self.start())
        self.say_goodbye()

    # User entrypoint code
    async def await_data(self):
        self.post_status_update(AgentState.AWAITING_PROMISE, "awaiting {} promises".format(self.attributes.num_promises()))
        await self.is_fullfilled.wait()
        
    async def run(self):
        raise NotImplementedError()
    
    async def _ping_loop(self):
        while not self._stopped():
            await asyncio.sleep(self.spec.pingInterval_ms/1000)
            self.send_ping()
        return False

    async def _message_thread(self):
        while not self._stopped():
            
            await asyncio.sleep(self.spec.pollInterval_ms/1000 + 0.5)
            
            msgs = self._get_messages(self.last_msg_idx+1) # list of messages
            
            if len(msgs) > 0:
                for msg in msgs:
                    
                    msg_type = msg.WhichOneof('contents')

                    if msg_type == "result":
                        # check if the result fulfills any of our promises
                        key, exists = self.attributes._contains(msg.result.promise)
                        
                        if exists:
                            self.attributes._fulfill(key, msg.result.promise)
                            
                        if self.attributes.all_fulfilled():
                            self.is_fullfilled.set()
                            
                    elif msg_type == "halt":
                        self.stop()
                        
                    self.last_msg_idx = msg.index
                    #self.last_msg_idx = msg["index"]
                    
        return False
    
    def stop(self):
        with self.mutex:
            self.stopped=True
            
    def _stopped(self):
        with self.mutex:
            return self.stopped
        
# This main runs some tests 
if __name__=="__main__":

    bb_addr = sys.argv[1]

    spec = pb2.AgentSpec(
        name="base-agent",
        pingInterval_ms=1000,
        pollInterval_ms=1000)

    a = AgentHTTP(spec, bb_addr)
    
    a.say_hello()
    a.send_ping()
    a.post_status_update(pb2.StatusUpdate.AgentState.Working, "starting some processing")
    a.log(pb2.Log.Severity.Info, "hello world")
    a.post_result("result_name", "result_type", {"hello":"world"})
    a.post_partial_result("partial_result_name", "partial_result_type", {"hello":"world"})
    a.post_no_result("no_result_name", "no_result_type", {"hello":"world"})
    print(a._get_messages(3))
    a.say_goodbye()

    #asyncio.run(a.start())
    