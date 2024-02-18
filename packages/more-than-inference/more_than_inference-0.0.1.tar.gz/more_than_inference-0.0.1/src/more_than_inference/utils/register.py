from typing import Callable


class METARegister:
    _instance = None
    registers = {}
    runners = {}
    cmds = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def regist(self, name=None):
        def decorator(cls: type):
            nonlocal name
            if name is None:
                name = cls.__name__
            assert name not in self.registers, f"cls name: `{name}` already registed."
            self.registers[name] = cls
            if not hasattr(cls, 'sub_classes'):
                cls.sub_classes = []
            return cls
        return decorator

    def regist_runner(self, name=None):
        def decorator(func: Callable):
            nonlocal name
            if name is None:
                name = func.__name__
            assert name not in self.runners, f"func name: `{name}` already registed."
            self.runners[name] = func
            setattr(func, "__runner_name__", name)
            return func
        return decorator

    def regist_cmd(self):
        def decorator(func: Callable):
            name = func.__name__
            assert name not in self.cmds, f"cmd name: `{name}` already registed."
            self.cmds[name] = func
            setattr(func, "__runner_name__", name)
            return func
        return decorator


META = METARegister()
