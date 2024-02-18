import atexit
import importlib
import multiprocessing.connection
from multiprocessing import Pipe
from multiprocessing.managers import DictProxy
from types import NoneType
from typing import Any, Callable

from loguru import logger

from more_than_inference.utils.fix_bug39959 import start_a_forkserver_process
from more_than_inference.utils.parser import CLI
from more_than_inference.utils.register import META


def add_runtime_path():
    import os
    import sys
    current_script_path = os.path.abspath('')
    if current_script_path not in sys.path:
        sys.path.append(current_script_path)


@META.regist_runner("ASYNC_OD")  # Drpc Async ObjectDetection
def runner_object_detection_async(args: CLI, inference_ally: DictProxy, pipe: multiprocessing.connection.Connection, unknown_args: Any = None):
    add_runtime_path()
    from more_than_inference.inference.object_detection import ObjectDetectionBase
    module = importlib.import_module(inference_ally["custom_class_module"])
    object_detection_class: type[ObjectDetectionBase] = getattr(module, inference_ally["custom_class_name"])
    object_detection_instance: ObjectDetectionBase = object_detection_class()
    object_detection_instance.store_args(args=args, unknown_args=unknown_args)
    object_detection_instance.load_model()
    atexit.register(object_detection_instance.unload_model)
    runner_name = getattr(runner_object_detection_async, "__runner_name__", "UNREGISTED_RUNNER")
    while True:
        logger.info(f"MTI::{runner_name}| WAITING ASYNC")
        try:
            object_detection_instance.run_async(pipe)
        except Exception:
            logger.exception(f"MTI::{runner_name}| EXCEPTION")
        logger.info(f"MTI::{runner_name}| INFER OVER")


@META.regist_runner("ASYNC_DRPC")
def runner_async_drpc(args: CLI, inference_ally: DictProxy, pipe: multiprocessing.connection.Connection, unknown_args: Any = None):
    from more_than_inference.extensions.drpc.object_detection import ObjectDetectionServer
    server = ObjectDetectionServer(args.port)
    runner_name = getattr(runner_object_detection_async, "__runner_name__", "UNREGISTED_RUNNER")
    logger.info(f"MTI::{runner_name}| DRPC SERVICE START")
    callback = server.run_async(pipe)
    server.run(callback)


def run_async(args: CLI, inference_ally: DictProxy, unknown_args=None):
    assert args.runner in META.runners, f"undefined runner `{args.runner}`"
    p1, p2 = Pipe()
    algo_runtime = start_a_forkserver_process(target=META.runners[args.runner], args=(args, inference_ally, p1, unknown_args))
    algo_runtime.start()
    server_runtime_name = f"ASYNC_{args.service}"
    logger.info(f"finding `{server_runtime_name}` in registed runners.")
    try:
        server_runtime_func: Callable[[CLI, DictProxy, multiprocessing.connection.Connection, Any],
                                      NoneType] = META.runners[server_runtime_name]
        logger.info(f"found `{server_runtime_name}` in registed runners.")
        server_runtime_func(args, inference_ally, p2, unknown_args)
    except KeyboardInterrupt as e:
        logger.info(f"EXIT WITH KeyboardInterrupt")
    except Exception as e:
        logger.error(f"error in trying execute runner `{server_runtime_name}` for reason: {e}, stack trace:")
        logger.exception(e)
    finally:
        algo_runtime.kill()
        algo_runtime.join()
    logger.info(f"OVER.")


def run_pipeline(args: CLI, inference_ally: DictProxy, unknown_args: Any = None):
    ...


def run(args: CLI, inference_ally, unknown_args: Any = None):
    if args.runner.startswith("ASYNC"):
        run_async(args, inference_ally, unknown_args)
    elif args.runner.startswith("PIPE"):
        run_pipeline(args, inference_ally, unknown_args)
    else:
        raise ValueError(f"unsupport runner mode `{args.runner}`")
