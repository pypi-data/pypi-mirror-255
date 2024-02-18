import multiprocessing.connection
from multiprocessing import shared_memory

import numpy as np

from more_than_inference.inference.meta import ArgParserMixin, InferMixin, MetaInference, ModuleMixin, RuntimeMixin
from more_than_inference.utils.register import META


class RunAsyncMixin:
    def run_async(self: RuntimeMixin, pipe: multiprocessing.connection.Connection):
        pipe_imgs = pipe.recv()
        rsts = []
        for pipe_image in pipe_imgs:
            shm_name, shm_shape, shm_dtype = pipe_image
            existing_shm = shared_memory.SharedMemory(name=shm_name)
            rsts.append(self.run(np.ndarray(shm_shape, dtype=shm_dtype, buffer=existing_shm.buf)))
            existing_shm.close()
        pipe.send(rsts)


class RunPipelineMixin:
    def run_pipeline(self: RuntimeMixin, pipe: multiprocessing.connection.Connection): ...


@META.regist(name="ObjectDetection")
class ObjectDetectionBase(ArgParserMixin,
                          ModuleMixin,
                          InferMixin,
                          RuntimeMixin,
                          RunAsyncMixin,
                          RunPipelineMixin,
                          metaclass=MetaInference):
    ...
