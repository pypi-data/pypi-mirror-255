# This script is a fix for python issue 39959 (https://bugs.python.org/issue39959)
import sys
from multiprocessing import get_context
from multiprocessing.context import BaseContext
from multiprocessing.process import BaseProcess


def start_a_naive_process(group=None, target=None, name=None, args: tuple = None, kwargs: dict = None, daemon=None,
                          method: str = None,) -> BaseProcess:
    ctx: BaseContext = get_context(method)
    P: BaseProcess = ctx.Process
    return P(group=group, target=target, name=name, args=args or (), kwargs=kwargs or {}, daemon=daemon)


def start_a_spawn_process(group=None, target=None, name=None, args: tuple = None, kwargs: dict = None, daemon=None) -> BaseProcess:
    return start_a_naive_process(group, target, name, args, kwargs, daemon, "spawn")


def start_a_fork_process(group=None, target=None, name=None, args: tuple = None, kwargs: dict = None, daemon=None) -> BaseProcess:
    return start_a_naive_process(group, target, name, args, kwargs, daemon, "fork")


def start_a_forkserver_process(group=None, target=None, name=None, args: tuple = None, kwargs: dict = None, daemon=None) -> BaseProcess:
    return start_a_naive_process(group, target, name, args, kwargs, daemon, "forkserver")


if sys.platform == "win32":
    start_a_fork_process = start_a_spawn_process
    start_a_forkserver_process = start_a_spawn_process
