import multiprocessing.connection
import os
from multiprocessing import Queue, shared_memory
from typing import Any

import numpy as np
from loguru import logger

from more_than_inference.datas.object_detection import ObjectDetectionInputSerializer, ObjectDetectionOutputSerializer
from more_than_inference.extensions.zmq.cs_base import ZeroMQClient, ZeroMQServer
from more_than_inference.utils.serializer import TypedNode, TypedPipeline


class ObjectDetectionServer(ZeroMQServer):
    def __init__(self, bind_addr: str, node_name: str, node_key: str, domain: str, node_category: str):
        super().__init__(bind_addr, node_name, node_key, domain)
        self.node_category = node_category

    def run_async(self, pipe: multiprocessing.connection.Connection,
                  typed_input: type[ObjectDetectionInputSerializer],
                  typed_output: type[ObjectDetectionOutputSerializer]):
        """`processing_async` run outside the inference process
        """
        def _get_input(_d: bytes):
            _inst = typed_input()
            _inst.loads(_d)
            return _inst

        def _get_output(output: Any) -> ObjectDetectionOutputSerializer:
            _inst = typed_output()
            _inst.result = output
            return _inst

        def processing_async(data_in: bytes) -> bytes:
            _input = _get_input(data_in)
            _image = _input.image
            if _image is None:
                return b'E: Image Decode Error.'
            shm = shared_memory.SharedMemory(create=True, size=_image.nbytes)
            shared_arr = np.ndarray(_image.shape, dtype=_image.dtype, buffer=shm.buf)
            np.copyto(shared_arr, _image)
            pipe.send((shm.name, _image.shape, _image.dtype))
            result = pipe.recv()
            shm.close()
            shm.unlink()
            output = _get_output(result)
            return output.dumps()
        return processing_async

    def run_pipeline(self, q_in: Queue, q_out: Queue):
        """`processing_input` run outside the inference process,
        `processing_output` run outside the inference process.
        """

        def _get_output(output: Any) -> TypedPipeline:
            _inst = TypedPipeline()
            _inst.result = output
            return _inst

        def processing_input(data_in: bytes) -> bytes:
            q_in.put(data_in)
            return b'I: OK'

        def processing_output(client: ObjectDetectionClient):
            while True:
                tp: TypedPipeline = q_out.get()
                if len(tp.StackList) == 0:
                    logger.info(f"Pipeline Ended, Key is {tp.Key}.")
                next_node = tp.StackList.pop()
                client.send_node(next_node, tp.dumps())

        return processing_input, processing_output


class ObjectDetectionClient(ZeroMQClient):
    def ipc_exists(self, sock: str):
        sock = sock.replace("ipc://", "")
        return os.path.exists(sock)

    async def send_node(self, node: TypedNode, data: bytes):
        sock = node.LocalSocket
        if not self.ipc_exists(sock):
            sock = node.RemoteSocket

        self.socket.connect(sock)
        await self.socket.send(data)
        reply = await self.socket.recv()
        self.socket.disconnect(sock)
        logger.info(reply)
        return reply


if __name__ == "__main__":
    import asyncio
    from multiprocessing import Pipe, Process

    import cv2

    from more_than_inference.datas.object_detection import TypedObjectDetectionArrayInput, TypedObjectDetectionPbOutput

    async def main():

        def process_pipe(pip_in: multiprocessing.connection.Connection):
            while True:
                shm_name, shm_shape, shm_dtype = pip_in.recv()
                logger.info(f"P: RECV {shm_name,shm_shape,shm_dtype}")
                existing_shm = shared_memory.SharedMemory(name=shm_name, create=False)
                shared_arr = np.ndarray(shm_shape, dtype=shm_dtype, buffer=existing_shm.buf)
                cv2.imwrite(shm_name+".png", shared_arr)
                existing_shm.close()
                pip_in.send({"key": "id:1",
                            "result": [{"type": "rectangle",
                                        "points": [0, 0, 152, 153],
                                        "confidence": 0.698,
                                        "label": "default"}]})

        ods = ObjectDetectionServer(
            bind_addr="ipc:///tmp/zero.sock",
            node_name="",
            node_key="",
            domain="",
            node_category="",
        )
        pipe_parent, pipe_child = Pipe()
        p = Process(target=process_pipe, args=(pipe_child,))
        p.start()
        processing_async = ods.run_async(pipe_parent, TypedObjectDetectionArrayInput, TypedObjectDetectionPbOutput)
        asyncio.create_task(ods.start(processing_async))

        await asyncio.sleep(1)

        din = TypedObjectDetectionArrayInput()
        din.image = cv2.imread("assets/Lenna.png")
        din.Key = "Lenna"

        odc = ObjectDetectionClient(bind_addr="",
                                    node_name="",
                                    node_key="",
                                    domain=""
                                    )
        node = TypedNode()
        node.LocalSocket = "ipc:///tmp/zero.sock"
        node.Key = "client"
        reply = await odc.send_node(node, din.dumps())
        dou = TypedObjectDetectionPbOutput()
        dou.loads(reply)
        print(dou.Key, dou.Result)
        p.join()

    asyncio.run(main())
