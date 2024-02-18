import asyncio
from typing import Callable

import zmq
import zmq.asyncio
from loguru import logger

from more_than_inference.protos.node_pb2 import Node


class ZeroMQServer:
    def __init__(self, bind_addr: str, node_name: str = None, node_key: str = None, domain: str = None):
        self.bind_addr = bind_addr
        self.node_name = node_name
        self.node_key = node_key
        self.domain = domain
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)

    async def start(self, callback_func: Callable[[bytes], bytes]):
        self.socket.bind(self.bind_addr)
        while True:
            message = await self.socket.recv()
            await self.socket.send(callback_func(message))


class ZeroMQClient:
    def __init__(self, bind_addr: str = None, node_name: str = None, node_key: str = None, domain: str = None):
        self.bind_addr = bind_addr
        self.node_name = node_name
        self.node_key = node_key
        self.domain = domain
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REQ)

    async def send(self, data: bytes, callback_func: Callable[["ZeroMQClient", bytes, bytes], bytes] = None):
        self.socket.connect(self.bind_addr)
        await self.socket.send(data)
        reply = await self.socket.recv()
        if callback_func is not None:
            logger.info(f"CONN TO `{self.bind_addr}` RECV BACK `{reply}`")
            callback_func(self, data, reply)
        self.socket.disconnect(self.bind_addr)


async def main():
    # Server
    def callback_func(inputs: bytes):
        node = Node()
        node.ParseFromString(inputs)
        print(node.Key)
        return b"OK"
    server = ZeroMQServer("ipc:///tmp/zero.sock", "local", "local", "local")
    asyncio.create_task(server.start(callback_func))

    # Give the server some time to start
    # await asyncio.sleep(1)

    # Client
    client = ZeroMQClient("ipc:///tmp/zero.sock", "local", "local", "local")
    node = Node(
        RemoteSocket="tcp://192.168.1.1:5555/",
        LocalSocket="/tmp/node",
        NodeName="ExampleNode",
        Domain="TEST",
        Category="ObjectDetection",
        Key="secretkey"
    )

    def callback_func(*args):
        print(*args)
        return
    await client.send(node.SerializeToString(), callback_func)

if __name__ == "__main__":
    asyncio.run(main())
