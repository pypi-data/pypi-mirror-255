from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy

from more_than_inference.runs import *
from more_than_inference.utils.build_proto import *
from more_than_inference.utils.module_functions import load_module_by_spec
from more_than_inference.utils.parser import CLI, apply_act, parse_act, parse_runner, parse_script, parse_service
from more_than_inference.utils.register import META


def run_cmd(args: CLI):
    if args.script in META.cmds:
        try:
            META.cmds[args.script](args)
        except:
            logger.exception(f"cmd `{args.script}` exec with error")
        finally:
            return True
    return False


def test_import(args: CLI, inference_ally: DictProxy):
    flag, msg = load_module_by_spec(args.script)
    logger.info(msg)
    if not flag:
        inference_ally["custom_class_flag"] = False
        return
    meta_class = META.registers[args.type]
    meta_class.print_inferences()
    custom_class = meta_class.get_inference(args.name, args.module)
    if custom_class is not None:
        inference_ally["custom_class_flag"] = True
        inference_ally["custom_class_name"] = custom_class.__name__
        inference_ally["custom_class_module"] = custom_class.__module__
    else:
        inference_ally["custom_class_flag"] = False


def run_script(args: CLI, unknown_args):
    manager = Manager()
    inference_ally: DictProxy = manager.dict()
    ally = Process(target=test_import, args=(args, inference_ally))
    ally.start()
    ally.join()
    logger.info(f"run_script:: inference_ally: {inference_ally}")
    if inference_ally["custom_class_flag"]:
        logger.info(f"run_script:: custom_class_name: {inference_ally['custom_class_name']}")
    else:
        raise ValueError(f"Model type '{args.type}' with name '{args.name}' not found.")

    run(args, inference_ally, unknown_args)


@META.regist_cmd()
def types(args): print("Support task types:", list(META.cmds.keys()))


def main():
    parser = parse_script()
    parser = parse_runner(parser)
    parser = parse_service(parser)
    parser = parse_act(parser)

    args, unknown_args = parser.parse_known_args()
    logger.info(f"cmd `{args.script}` args `{args}`, unknown_args `{unknown_args}` start")
    args: CLI
    # reconfig act args
    args = apply_act(args, unknown_args)

    if run_cmd(args):
        logger.info(f"cmd `{args.script}` args `{args}` over")
    elif args.script.endswith(".py"):
        run_script(args, unknown_args)
    else:
        raise ValueError(f"not support command `{args.script}` current support is: {list(META.cmds.keys())}")


if __name__ == "__main__":
    main()
