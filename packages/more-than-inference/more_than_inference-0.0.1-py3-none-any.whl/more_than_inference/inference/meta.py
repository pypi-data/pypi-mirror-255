from abc import abstractmethod
from typing import Any

from loguru import logger

from more_than_inference.utils.register import META


class MetaInference(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        for _, meta in META.registers.items():
            if meta in bases:
                meta.sub_classes.append(new_class)
        return new_class


class ModuleMixin:
    """This Mixin provide operations for find and get subclass of registed MetaInference"""
    @classmethod
    def print_inferences(cls):
        """Print all inferences that registed in MetaInference
        """
        for subclass in cls.sub_classes:
            logger.info("loaded:: "+subclass.__module__ + '.' + subclass.__name__)

    @classmethod
    def get_inference(cls, name: str = None, module: str = None):
        """Get inference from registed
        """
        collects = []
        for subclass in cls.sub_classes:
            if name is None:
                collects.append(subclass)
            else:
                if module not in [None, subclass.__module__]:
                    continue
                if name == subclass.__name__:
                    collects.append(subclass)
        if len(collects) == 0:
            print(f"get none of this inference module=`{module}` name=`{name}`")
            return
        elif len(collects) > 1:
            print(f"get more than one inference in module=`{module}` name=`{name}`, result=[{collects}], "
                  f"would choose `{collects[0]}` as default.")
        return collects[0]


class InferMixin:
    """This Mixin contains load/unload model and preprocess/postprocess/predict data from inference."""
    @abstractmethod
    def load_model(self, *args, **kwargs): raise NotImplementedError
    @abstractmethod
    def unload_model(self, *args, **kwargs): raise NotImplementedError
    @abstractmethod
    def preprocess(self, data: Any, *args, **kwargs): raise NotImplementedError
    @abstractmethod
    def postprocess(self, data: Any, *args, **kwargs): raise NotImplementedError
    @abstractmethod
    def predict(self, data: Any, *args, **kwargs): raise NotImplementedError


class RuntimeMixin:
    def run(self, data: Any, *args, **kwargs):
        data = self.preprocess(data, *args, **kwargs)
        data = self.predict(data, *args, **kwargs)
        data = self.postprocess(data, *args, **kwargs)
        return data


class ArgParserMixin:
    def store_args(self, args=None, unknown_args=None) -> None:
        self.args = args
        self.unknown_args = unknown_args
