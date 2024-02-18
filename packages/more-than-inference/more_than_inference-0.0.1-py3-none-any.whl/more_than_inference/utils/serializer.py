import builtins
from abc import abstractmethod
from typing import Any, Callable, TypeVar, get_args, get_origin

import google.protobuf.message

from more_than_inference.protos.data_pb2 import Data
from more_than_inference.protos.node_pb2 import Node
from more_than_inference.protos.pipeline_pb2 import Pipeline

# ---------------------------------------------------------------------------------------------------------------------
# Serialize Functions
# ---------------------------------------------------------------------------------------------------------------------
_T = TypeVar("_T")
_VT = TypeVar("_VT")
_BUILTINS = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]


class ProtoLoadsMixin:
    def loads(T: _T, data_class: type[google.protobuf.message.Message]) -> Callable[[bytes], _T]:
        def _call_stack(_t: type, _d: Any, self=None):
            if _t in _BUILTINS:
                return _d
            if self is None:
                _i = _t()
            else:
                _i = self
            for field in _t._protected:
                if field not in _t._registed:
                    setattr(_i, field, getattr(_d, field))
                else:
                    registed_type = _t._registed[field]
                    origin_type = get_origin(registed_type)
                    if origin_type is None:
                        setattr(_i, field, _call_stack(registed_type, getattr(_d, field)))
                    elif origin_type == list:
                        item_type = get_args(registed_type)[0]
                        setattr(_i, field, [_call_stack(item_type, __i) for __i in getattr(_d, field)])
                    else:
                        raise ValueError(f"unsupport origin type `{origin_type}` for `{registed_type}`")
            return _i

        def _loads(self: _T, data: bytes) -> _T:
            _inst = data_class()
            _inst.ParseFromString(data)
            return _call_stack(T, _inst, self=self)
        return _loads


class ProtoDumpsMixin:
    def dumps(T: _T, data_class: type[google.protobuf.message.Message]) -> Callable[[_T], bytes]:
        def _call_stack(_t: type, _d: Any, _inst: _VT = None) -> _VT:
            if _t in _BUILTINS:
                return _d
            if _inst is None:
                _inst = _t._data_class()
            for field in _t._protected:
                if not hasattr(_d, field):
                    continue
                if field not in _t._registed:
                    setattr(_inst, field, getattr(_d, field))
                else:
                    registed_type = _t._registed[field]
                    origin_type = get_origin(registed_type)
                    if origin_type is None:
                        _call_stack(registed_type, getattr(_d, field), getattr(_inst, field))
                    elif origin_type == list:
                        item_type = get_args(registed_type)[0]
                        for __i in getattr(_d, field):
                            getattr(_inst, field).append(_call_stack(item_type, __i))
                    else:
                        raise ValueError(f"unsupport origin type `{origin_type}` for `{registed_type}`")
            return _inst

        def _dumps(self: _T) -> bytes:
            _inst = _call_stack(T, self, data_class())
            return _inst.SerializeToString()
        return _dumps

# TODO: Json implymention


class JsonLoadsMixin:
    def loads():
        ...


class JsonDumpsMixin:
    def dumps():
        ...


# ---------------------------------------------------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------------------------------------------------
class BaseSerializer:
    @abstractmethod
    def loads(data: bytes) -> Any: raise NotImplementedError
    @abstractmethod
    def dumps(data: Any) -> bytes: raise NotImplementedError


class MetaSerializer(type):
    def __new__(cls: type, name: str, bases: tuple, attrs: dict):
        new_class = super().__new__(cls, name, bases, attrs)
        _data_class = attrs.get('_data_class', None)  # `_data_class` defined the main protocol class in use
        _protected = attrs.get('_protected', None)  # `_protected` defined the field to serialize
        _registed = attrs.get('_registed', None)  # `_registed` defined the field already registed
        if _data_class is not None:
            setattr(new_class, 'loads', cls.loads(new_class, _data_class))
            setattr(new_class, 'dumps', cls.dumps(new_class, _data_class))
        # set default value
        if _protected is None:
            setattr(new_class, '_protected', attrs['__annotations__'].keys())
        if _registed is None:
            setattr(new_class, '_registed', {})
        return new_class


class ProtoSerializer(ProtoLoadsMixin, ProtoDumpsMixin, MetaSerializer):
    """This Class is a MetaClass, provide the loads/dumps function to childs, Backend support proto.
    To enable using loads/dumps function, define class var `_data_class`. Define class var `_protected`
    should give those specified key data to transfer.
    """
    ...


# ---------------------------------------------------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------------------------------------------------
class TypedData(BaseSerializer, metaclass=ProtoSerializer):
    _data_class = Data

    Body: builtins.bytes
    Serializer: builtins.str
    Seq: builtins.int
    Ended: builtins.bool


class TypedNode(BaseSerializer, metaclass=ProtoSerializer):
    _data_class = Node

    RemoteSocket: builtins.str
    LocalSocket: builtins.str
    NodeName: builtins.str
    Domain: builtins.str
    Category: builtins.str
    Key: builtins.str


class TypedPipeline(BaseSerializer, metaclass=ProtoSerializer):
    _data_class = Pipeline
    _registed = {"StackList": list[TypedNode], "Data": TypedData}

    Key: builtins.str
    StackList: list[TypedNode]
    Data: TypedData


if __name__ == "__main__":
    data = TypedData()
    data.Body = b''
    data.Serializer = "hello"
    data.Seq = 0
    data.Ended = False
    bdata = data.dumps()
    print(bdata)

    cdata = TypedData()
    cdata.loads(bdata)
    print(cdata.Serializer)
    print(get_args(list[TypedNode]))
    print(get_origin(TypedNode))

    tp = TypedPipeline()
    tp.Data = TypedData()
    tp.Data.Body = b'\n\x04KKKK\x12\n\x1a\x03GGG2\x03SST\x1a\x05\x12\x03DIM'
    tp.Data.Ended = False
    tp.Data.Seq = 0
    tp.Data.Serializer = "DIM"
    tp.StackList = []
    node = TypedNode()
    node.Category = "SST"
    node.LocalSocket = "GGG"
    tp.StackList.append(node)
    tp.Key = "KKKK"

    ss = tp.dumps()
    print(ss)

    ttp = TypedPipeline()
    ttp.loads(ss)
    print(ttp.StackList[0].LocalSocket)
    print(ttp.Data.Serializer)
