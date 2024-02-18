import argparse
import builtins

class RUNNER_CLI:
    type:builtins.str
    name:builtins.str 
    module:builtins.str 
    runner:builtins.str
    service:builtins.str

class SERVICE:
    port:builtins.int
class ACT:
    act_model_path:builtins.str 
    act_used_model:builtins.str
    act_service_port:builtins.int
class CLI:
    script:str

    type:builtins.str
    name:builtins.str 
    module:builtins.str 
    runner:builtins.str
    service:builtins.str
    
    port:builtins.int

    act_model_path:builtins.str
    act_used_model:builtins.str
    act_service_port:builtins.int

def parse()->argparse.ArgumentParser: ...
def parse_runner(parser: argparse.ArgumentParser)->argparse.ArgumentParser: ...
def parse_service(parser: argparse.ArgumentParser)->argparse.ArgumentParser: ...
def parse_act(parser: argparse.ArgumentParser)->argparse.ArgumentParser: ...
def parse_script(parser: argparse.ArgumentParser)->argparse.ArgumentParser: ...
def apply_act(args: CLI)->CLI: ...