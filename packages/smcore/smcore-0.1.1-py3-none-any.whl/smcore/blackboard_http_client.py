import io

import json
import pycurl
from google.protobuf import json_format

from . import types_pb2 as pb2

class BlackboardHTTPClient:

    c = pycurl.Curl()

    def __init__(self, addr):
        # instantiate a channel
        # bind the client and the server
        self.addr = addr
        
    def _get_messages(self, starting_at, filter_pings=True):
        url = "http://{}/blackboard/{}".format(self.addr, starting_at)
        
        buff = io.BytesIO()
        self.c.setopt(self.c.URL, url)
        self.c.setopt(self.c.WRITEDATA, buff)
        self.c.perform()
        self.c.reset()

        body = buff.getvalue()
        msgs = json.loads(body.decode("utf-8"))
        
        # Translate from dictionary
        msg_stack = json_format.ParseDict(msgs, pb2.MessageStack())
        return msg_stack.messages

    def _get_result_messages(self, starting_at):
        url = "http://{}/result/{}".format(self.addr, starting_at)
        
        buff = io.BytesIO()
        self.c.setopt(self.c.URL, url)
        self.c.setopt(self.c.WRITEDATA, buff)
        self.c.perform()
        self.c.reset()

        body = buff.getvalue()
        msgs = json.loads(body.decode("utf-8"))
        
        # Translate from dictionary
        msg_stack = json_format.ParseDict(msgs, pb2.MessageStack())
        return msg_stack.messages

    def _send_message(self, msg):
        url = "http://{}/message".format(self.addr)
        msg_json = json_format.MessageToJson(msg)
        
        self.c.setopt(self.c.URL, url)
        self.c.setopt(self.c.UPLOAD, 1)
        self.c.setopt(self.c.READDATA, io.StringIO(msg_json))
        self.c.perform()
        self.c.reset()
        
