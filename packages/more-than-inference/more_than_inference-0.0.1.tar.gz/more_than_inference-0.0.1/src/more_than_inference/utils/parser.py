import argparse
import sys
from dataclasses import dataclass, is_dataclass
from typing import Any, Dict, Type


def shallow_asdict(obj: Any) -> Dict[str, "ARG"]: return {field.name: getattr(obj, field.name)
                                                          for field in obj.__dataclass_fields__.values()} if is_dataclass(obj) else obj


@dataclass(frozen=True)
class ARG:
    short: str = None
    type: Type = str
    required: bool = False
    default: Any = None
    help: str = None

    def get_args(self, long: str): return [f"-{self.short}", f"--{long}"] if self.short else [f"--{long}"]
    def apply_args(self, val: Any): return [f"--{self.long}", val]


def parse_ln(ln: Dict[str, ARG], parser: argparse.ArgumentParser = None):
    if not parser:
        parser = argparse.ArgumentParser()
    for varg_name, varg in ln.items():
        parser.add_argument(*varg.get_args(long=varg_name), type=varg.type, required=varg.required,
                            default=varg.default, help=varg.help)
    return parser


@dataclass(frozen=True)
class RUNNER_CLI:
    type: ARG = ARG(short='t', type=str, default="ObjectDetection",
                    help='cli:: Model type, or task flag, default is `ObjectDetection`')
    name: ARG = ARG(short='n', type=str,
                    help='cli:: Model name, a specified name of the model, such as `CustomYOLO`, if not defined, cli whould use the first searched as default')
    module: ARG = ARG(short='m', type=str,
                      help='cli:: Model module, specify if name is used, help the cli locate the class, if not defined, behave as `cli:: name`.')
    runner: ARG = ARG(short='r', type=str, default="ASYNC_OD",
                      help='cli:: Runtime runner, default is `ASYNC_OD`, function defined in `more_than_inference/runs.py`, must start with ASYNC/PIPE')
    service: ARG = ARG(short='s', type=str, default="DRPC",
                       help='cli:: Runtime backend service, default is `DRPC`, enabled with extension installed')


@dataclass(frozen=True)
class SERVICE:
    port: ARG = ARG(type=int, default=3963, help='service:: service port')


@dataclass(frozen=True)
class ACT:
    act_model_path: ARG = ARG(type=str, help='act:: directory of the model')
    act_used_model: ARG = ARG(type=str, help='act:: name of the model(no ext)')
    act_service_port: ARG = ARG(type=int, help='act:: service port, if use, this will replace `service:: port`')


class CLI(RUNNER_CLI,
          SERVICE,
          ACT):
    script: str


def parse(): return argparse.ArgumentParser()
def parse_runner(parser: argparse.ArgumentParser = None): return parse_ln(shallow_asdict(RUNNER_CLI()), parser=parser)
def parse_service(parser: argparse.ArgumentParser = None): return parse_ln(shallow_asdict(SERVICE()), parser=parser)
def parse_act(parser: argparse.ArgumentParser = None): return parse_ln(shallow_asdict(ACT()), parser=parser)


def parse_script(parser: argparse.ArgumentParser = None):
    if not parser:
        parser = argparse.ArgumentParser()
    parser.add_argument(
        'script', help=f'Script to load models, or cli to do something, use `{sys.argv[0]} types` to list all cli')
    return parser


def apply_act(args: CLI, unknown_args: Any) -> CLI:
    parser_unknown = argparse.ArgumentParser()
    parser_unknown.add_argument("--service_port", type=int)
    unknown_args, _ = parser_unknown.parse_known_args(unknown_args)

    if args.act_service_port is None and unknown_args.service_port is None:
        return args
    setattr(args, "port", args.act_service_port or unknown_args.service_port)
    return args
