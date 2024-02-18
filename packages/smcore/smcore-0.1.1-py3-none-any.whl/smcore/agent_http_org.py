import sys
from message_types import *
import datetime
import urllib.request, urllib.parse
import json
from threading import Lock
import asyncio
import time

import grpc
import types_pb2 as pb2
import types_pb2_grpc as pb2_grpc


def HTTPGet(url):
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request) as f:
        return f.read().decode("utf-8")


def HTTPPost(url, msg):
    # data = urllib.parse.urlencode(data)
    data_str = msg.toJSON()
    data = data_str.encode("utf-8")
    request = urllib.request.Request(url)

    print("Posting data to url: ", url, data)
    with urllib.request.urlopen(request, data) as f:
        return f.read().decode("utf-8")


class Agent(AgentSpec):
    blackboard_remote_addr = ""
    last_msg_idx = 0
    stopped = False
    mutex = Lock()

    def __init__(self, spec, bb_addr):
        channel = grpc.insecure_channel("localhost:50051")
        stub = route_guide_pb2_grpc.RouteGuideStub(channel)

        self = spec
        self.blackboard_remote_addr = bb_addr
        self.start()

    # Primary Agent interface that users should employ when writing
    # their own agents
    def log(self, severity: LogSeverity, message: str):
        log_message = {"severity": str(severity), "message": message}
        log_string = json.dumps(log_message)
        self.send_message(MessageType.LOG, log_string)

    def post_status_update(self, state: AgentState, update: str):
        status_update = {"state": str(state), "message": update}
        update_string = json.dumps(status_update)
        self.send_message(MessageType.STATUSUPDATE, update_string)

    def post_result(self, res_name: str, res_type: str, data: dict):
        json_data = json.dumps(data)

        promise = {
            "dataidentifier": res_name,
            "promisetype": res_type,
            "source": self.Name,
            "data": json_data,
        }

        json_promise = json.dumps(promise)

        self.send_message(MessageType.RESULT, json_promise)

    def post_partial_result(self, res_name: str, res_type: str, data: dict):
        json_data = json.dumps(data)

        promise = {
            "dataidentifier": res_name,
            "promisetype": res_type,
            "source": self.Name,
            "data": json_data,
        }

        json_promise = json.dumps(promise)

        self.send_message(MessageType.PARTIALRESULT, json_promise)

    # Users should not generally need to call these methods directly, as
    # they are handled by the base class, however they are available if needed
    def send_ping(self):
        self.send_message(MessageType.PING, "")

    def say_hello(self):
        self.send_message(MessageType.HELLO, "")

    def say_goodbye(self):
        self.send_message(MessageType.GOODBYE, "")

    # send_messages sends a message to the configured blackboard (via the HTTP
    # interface).  In general, users should try  to prefer the higher-level methods
    # (such as post_status_update, log, post_result, etc.)
    #
    # msg_type should be one of those specified in message_types.py
    # data should be the marshaled JSON string (not bytes) of your message content
    def send_message(self, msg_type: MessageType, data: str):
        msg = Message(msg_type, data)
        msg.Type = msg_type
        msg.Source = self.Name
        msg.Data = data.encode("utf-8")
        msg.TimeSent = datetime.datetime.now(datetime.timezone.utc)
        self._post_message_http(msg)

    def _post_message_http(self, msg: Message):
        url = "http://" + self.blackboard_remote_addr + "/message"
        HTTPPost(url, msg)

    def _get_messages_http(self):
        with self.mutex:
            start_idx = self.last_msg_idx + 1
            url = (
                "http://"
                + self.blackboard_remote_addr
                + "/blackboard/"
                + str(start_idx)
            )
        r = HTTPGet(url)

        return json.loads(r)

    def _get_result_messages_http(self):
        # There's currently not a great way to lock last_msg_index between _get_result_messages and _get_messages,
        # which is something we have to think about together.
        with self.mutex:
            start_idx = self.last_msg_idx + 1
            url = "http://" + self.blackboard_remote_addr + "/result/" + str(start_idx)
        r = HTTPGet(url)

        return json.loads(r)

    async def start(self):
        await asyncio.gather(
            self._ping_loop(),
            self._message_thread(),
        )

    async def _ping_loop(self):
        while not self._stopped():
            await asyncio.sleep(self.PingInterval_ms / 1000)
            self.send_ping()
        return False

    async def _message_thread(self):
        while not self._stopped():
            await asyncio.sleep(self.PollInterval_ms / 1000 + 0.5)

            msgs = self._get_messages_http()  # list of messages
            if msgs != None:
                for msg in msgs:
                    self.last_msg_idx = msg["index"]

            # result_msgs = self._get_result_messages_http()  # list of messages
            # if msgs != None:
            #     for msg in msgs:
            #         self.last_msg_idx = msg["index"]

        return False

    def _stopped(self):
        with self.mutex:
            return self.stopped


# This main runs some tests
if __name__ == "__main__":
    a = Agent(sys.argv[1], "localhost:8080")
    # a = Agent("python-baby!", "localhost:8080")

    # a._get_messages_http()
    # a.say_hello()
    # a.send_ping()
    # a.post_status_update(AgentState.WORKING, "starting some processing")
    # a.log(LogSeverity.INFO, "some logging")
    # a.post_result("result_name", "result_type", '{"hello":"world"}')
    # a.say_goodbye()

    asyncio.run(a.start(), a.run())
