import base64
import multiprocessing.connection
from multiprocessing import shared_memory
from typing import Callable, Dict, List

import cv2
import numpy as np
from loguru import logger
from requests import Session

from more_than_inference.extensions.drpc.server_base import DrpcServer


class ObjectDetectionServer(DrpcServer):
    async def predict(self, images, image_type) -> Dict:
        """
        HTTP: /predict POST,GET
        """
        imgs = []
        if image_type == 'url':
            for image in images:
                with Session() as client:
                    resp = await client.get(image)
                    byte_content = await resp.read()
                image = np.asarray(bytearray(byte_content), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                imgs.append(image)
        elif image_type == 'image':     # act前端 base64
            for image in images:
                image_data = base64.b64decode(image)
                image_array = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                imgs.append(image)
        else:
            raise ValueError(f'image_type is invalid!')

        result = self._callback_func(imgs)
        logger.info(f"RET: {result}")
        return result

    def run_async(self, pipe: multiprocessing.connection.Connection):
        def processing_async(imgs: list[np.ndarray]) -> dict:
            shms: list[shared_memory.SharedMemory] = []
            sends: List[tuple] = []
            for img in imgs:
                shm = shared_memory.SharedMemory(create=True, size=img.nbytes)
                shared_arr = np.ndarray(img.shape, dtype=img.dtype, buffer=shm.buf)
                np.copyto(shared_arr, img)
                shms.append(shm)
                sends.append((shm.name, img.shape, img.dtype))

            pipe.send(sends)
            result = pipe.recv()
            for shm in shms:
                shm.close()
                shm.unlink()
            return result
        return processing_async

    def run(self, callback: Callable):
        self._callback_func = callback
        super().run()
