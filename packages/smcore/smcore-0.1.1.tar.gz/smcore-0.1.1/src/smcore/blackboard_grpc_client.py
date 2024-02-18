import sys

import grpc
import types_pb2 as pb2
import types_pb2_grpc as pb2_grpc

class BlackboardGRPCClient():
    def __init__(self, addr):
        # instantiate a channel
        # bind the client and the server
        self.addr = addr
        self.channel = grpc.insecure_channel(self.addr)
        self.stub = pb2_grpc.BlackboardHandlerStub(self.channel)

    def _get_messages(self, starting_at, filter_pings = True):
        msg_stack = self.stub.GetMessages(pb2.GetMessagesRequest(startingAt=starting_at, filterPings=filter_pings))
        return msg_stack.messages # iterable list of messages

    def _send_message(self, msg):
        self.stub.SendMessage(msg)

if __name__=="__main__":

    addr = sys.argv[1]
    
    b = BlackboardGRPCClient(addr)

    b.get_messages(0)