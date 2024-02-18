# Author  : Shenchucheng
import abc
import asyncio
import datetime
import inspect
import io
import json
import os
import socket
import ssl
import traceback
import typing
from concurrent.futures.thread import ThreadPoolExecutor
from contextvars import ContextVar
from functools import partial
from time import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import urlparse
from urllib.request import urlopen
from uuid import UUID, uuid4

import yaml
from aiohttp.web import Application, AppRunner, Request, Response, SockSite
from aiohttp.web import json_response as _json_response
from aiohttp.web_request import FileField
from loguru import logger


def load_stream(config: str, encoding="utf-8") -> str:
    path = config
    url_scheme = urlparse(path).scheme
    if url_scheme == "file":
        file = urlparse(path).netloc + urlparse(path).path
        with open(file, encoding=encoding) as fh:
            data = fh.read()
    elif url_scheme in ("http", "https"):
        data = urlopen(path).read()
    elif len(url_scheme) <= 1 and os.path.isfile(path):
        with open(path, encoding=encoding) as fh:
            data = fh.read()
    else:
        data = config
    if isinstance(data, bytes):
        data = data.decode(encoding)
    return data


def load_config(config, encoding: str = "utf-8"):
    if isinstance(config, str):
        data = load_stream(config, encoding)
        config = yaml.load(data, Loader=yaml.SafeLoader)
    if not isinstance(config, dict):
        raise TypeError("got incorrect value for config")

    return config


class BaseService(object):

    __drpc__: Union[Callable, bool]
    __rpc__: Union[Callable, bool]
    __http__: Union[Callable, bool]

    __http_uri_prefix__: str = ""
    __http_uri__: str = ""


class DefaultService(BaseService):

    __http_uri_prefix__ = ""
    __http__ = False
    __rpc__ = False

    def __init__(
        self,
        methods,
        http_enable: bool = True,
        rpc_enable: bool = False,
    ) -> None:
        self.http_enable = http_enable
        if http_enable:
            for method in methods:
                if hasattr(method, "__http__"):
                    continue
                format_http(method)
                self.add_method(method)
            self.__http__ = True
            self.__rpc__ = False
        else:
            raise ValueError
        self.__drpc_methods__ = methods

    def add_method(self, method: Callable):
        setattr(self, method.__name__, method)


def rpc(
    func: Optional[Callable] = None,
    request: Optional[Union[Callable, str]] = None,
    response: Optional[Union[Callable, str]] = None,
    name: Optional[Union[Callable, str]] = None,
    error: Optional[Union[Callable, str]] = None,
    rpc: bool = True,
):
    def wrap(func):
        func.__rpc__ = rpc

        if rpc is False:
            for attr in __rpc_attr__:
                if hasattr(func, attr):
                    delattr(func, attr)
            return func

        if isinstance(func, type):
            __rpc_cls__.add(func)
            return func

        func.__rpc_request__ = request
        func.__rpc_response__ = response
        func.__rpc_name__ = name
        func.__rpc_error__ = error
        return func

    wrap.__name__ = "rpc"
    if func is None:
        return wrap
    return wrap(func)


class BaseServer(abc.ABC):

    _http_enable = False
    _rpc_enable = False
    _executor_pools: Optional[ThreadPoolExecutor] = None
    _init_kwargs: Optional[Dict] = None
    DEBUG: bool = False

    def __init__(self) -> None:
        super().__init__()
        self._drpc_services = list()
        self._drpc_methods = list()

    def _init_executor_pool(self, executor_workers: Optional[int] = None) -> ThreadPoolExecutor:
        if executor_workers:
            self._executor_pools = ThreadPoolExecutor(executor_workers)
        return self._executor_pools

    def register(self, service: Any, **kwargs) -> None:
        """Register service cls or obj into server.

        Args:
            service (Any): service cls or obj
        """
        if inspect.isfunction(service) or inspect.iscoroutinefunction(service):
            self._drpc_methods.append(service)
        else:
            self._drpc_services.append(service)

        if self._http_enable:
            self.http_register(service, **kwargs)

        if self._rpc_enable:
            self.rpc_register(service, **kwargs)

    def http_register(self, server: Any, **kwargs) -> None:
        """Register server cls or obj into http server.

        Args:
            server (Any): server cls or obj

        Raises:
            NotImplementedError: Subclasses should implement this method.
        """
        raise NotImplementedError

    def rpc_register(self, server: Any, **kwargs) -> None:
        """Register server cls or obj into rpc server.

        Args:
            server (Any): server cls or obj

        Raises:
            NotImplementedError: Subclasses should implement this method.
        """
        raise NotImplementedError

    async def create_server(self, http: Optional[Dict] = None, rpc: Optional[Dict] = None, **kwargs) -> None:
        """Init the server."""
        if self._drpc_methods:
            default_service = DefaultService(self._drpc_methods, self._http_enable, self._rpc_enable)
            self._drpc_services.append(default_service)

        for i in range(len(self._drpc_services)):
            service = self._drpc_services[i]
            if isinstance(service, type):
                # TODO check only args
                try:
                    service = service(**self._init_kwargs)
                except Exception:
                    logger.info("init service error")
                    service = service()
                self._drpc_services[i] = service
            if not hasattr(service, "__drpc_methods__"):
                methods = list()
                for method in dir(service):
                    if method.startswith("_"):
                        continue
                    method = getattr(service, method)
                    if not callable(method) or method == service:
                        continue
                    methods.append(method)
                service.__drpc_methods__ = methods

        if self._http_enable:
            await self.create_http_server(http=http, **kwargs)
        if self._rpc_enable:
            await self.create_rpc_server(rpc=rpc, **kwargs)

    async def create_http_server(self, http: Optional[Dict] = None, **kwargs) -> None:
        """Init the http server.

        Args:
            http (Optional[Dict], optional): http server configuration. Defaults to None.

        Raises:
            NotImplementedError: Subclasses should implement this method.
        """
        raise NotImplementedError

    async def create_rpc_server(self, rpc: Dict, **kwargs) -> None:
        """Init the rpc server.

        Args:
            rpc (Optional[Dict], optional): rpc server configuration. Defaults to None.

        Raises:
            NotImplementedError: Subclasses should implement this method.
        """
        raise NotImplementedError

    async def start(
        self,
        http: Optional[Dict] = None,
        rpc: Optional[Dict] = None,
        init_kwargs: Optional[Dict] = None,
        executor_workers: int = 0,
        probe: Union[bool, Any] = False,
        **kwargs
    ) -> None:
        """Initial and start the server.

        Args:
            http (Optional[Dict], optional): http server configuartion. Defaults to None.
            rpc (Optional[Dict], optional): rpc server configuartion. Defaults to None.
            init_kwargs (Optional[Dict], optional): the server cls init kwargs. Defaults to None.
            executor_workers (int, optional): executor workers number. Defaults to 0.
            probe (Union[bool, Any], optional): whether to enable probe. Defaults to True.
        """
        if probe:
            # if probe is True:
            #     from drpc.component.probe import Probe as probe
            # self.register(probe)
            ...

        if executor_workers:
            self._init_executor_pool(executor_workers)

        self._init_kwargs = init_kwargs or dict()
        await self.create_server(http=http, rpc=rpc, **kwargs)

        async with self:
            while 1:
                await asyncio.sleep(3600)

    def run(
        self,
        *args,
        config: Optional[Union[Dict, str]] = None,
        log: Optional[Dict] = None,
        http: Optional[Dict] = None,
        rpc: Optional[Dict] = None,
        init_kwargs: Optional[Dict] = None,
        debug: bool = False,
        loop: Optional[asyncio.BaseEventLoop] = None,
        **kwargs
    ) -> None:
        """Run the server from configuration.

        Args:
            config (Optional[Union[Dict, str]], optional): the server configuration. Defaults to None.
            log (Optional[Dict], optional): log configuration. Defaults to None.
            http (Optional[Dict], optional): http server configuration. Defaults to None.
            rpc (Optional[Dict], optional): rpc server configuration. Defaults to None.
            init_kwargs (Optional[Dict], optional): the server cls init kwargs. Defaults to None.
            debug (bool, optional): start with debug mode. Defaults to False.
            loop (Optional[asyncio.BaseEventLoop], optional): the event loop to run this server. Defaults to None.
        """
        self.DEBUG = debug
        if config is not None:
            config = load_config(config)
            return self.run(config=None, **config)
        if log is None:
            log = dict()
        if http is None:
            http = dict()
        if rpc is None:
            rpc = dict()
        for key in tuple(kwargs.keys()):
            if key.startswith("log_"):
                log[key[4:]] = kwargs.pop(key)
            if key.startswith("http_"):
                http[key[5:]] = kwargs.pop(key)
            if key.startswith("rpc_"):
                rpc[key[4:]] = kwargs.pop(key)
        if debug:
            log["level"] = 10

        if args:
            method, *args = args
            if hasattr(self, method):
                method = getattr(self, method)
            else:
                raise ValueError("参数：{}无效".format(method))
            return method(*args, **kwargs)

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start(http, rpc, init_kwargs=init_kwargs, **kwargs))
        except KeyboardInterrupt:
            loop.run_until_complete(self.__aexit__(None, None, None))

    async def __aenter__(self):
        aenter = dict()
        for service in self._drpc_services:
            if hasattr(service, "__aenter__"):
                aenter[service.__aenter__.__func__] = service.__aenter__
        if aenter:
            await asyncio.gather(*(i() for i in aenter.values()))
        return self

    async def __aexit__(self, *args, **kwargs):
        if hasattr(self, "rpc_server") and self.rpc_server:
            try:
                await self.rpc_server.stop(1)
            except Exception:
                logger.error("stop rpc error", exc_info=True)
        aexit = dict()
        for service in self._drpc_services:
            if hasattr(service, "__aexit__"):
                aexit[service.__aexit__.__func__] = service.__aexit__
        if aexit:
            await asyncio.gather(*(i(*args, **kwargs) for i in aexit.values()), return_exceptions=True)
        if self._executor_pools:
            self._executor_pools.shutdown(True)


METHODS_ALLOW = ("GET", "POST", "DELETE", "PATCH", "PUT", "OPTIONS", "HAED")


def format_uri(uri: str) -> str:
    uri = uri.lower().replace(".", "/")
    if not uri.startswith("/"):
        uri = "/" + uri
    return uri


def format_method(method: str) -> str:
    method = method.strip().upper()
    if method not in METHODS_ALLOW:
        raise ValueError("method {} is not allowed".format(method))
    return method


__rpc_cls__ = set()
__rpc_attr__ = ("__rpc_request__", "__rpc_response__", "__rpc_error__", "__rpc_name__")

__http_cls__ = set()
__http_attr__ = (
    "__http_uri__",
    "__http_methods__",
    "__http_request__",
    "__http_response__",
    "__http_error__",
)


def _httpify(method: Callable):
    doc = method.__doc__
    kwargs = dict()
    if not doc:
        return kwargs
    for line in doc.splitlines():
        line = line.strip()
        if line.startswith("HTTP: /") or line.startswith("DRPC: /"):
            uri, *args = line[6:].split()
            methods, request, response, error, *_ = [*args, *(None for _ in range(4))]
            kwargs["uri"] = uri
            kwargs["methods"] = methods
            kwargs["request"] = request
            kwargs["response"] = response
            kwargs["error"] = error
    return kwargs


def format_http(
    func: Optional[Callable] = None,
    uri: Optional[str] = None,
    methods: Optional[List[str]] = None,
    request: Optional[Union[Callable, str]] = None,
    response: Optional[Union[Callable, str]] = None,
    error: Optional[Union[Callable, str]] = None,
    http: Optional[Union[Callable, str]] = None,
):
    def wrap(func: Callable):
        nonlocal uri, methods, request, response, error

        func.__http__ = http

        if http is False:
            for attr in __http_attr__:
                if hasattr(func, attr):
                    delattr(func, attr)
            return func

        if isinstance(func, type):
            __http_cls__.add(func)
            return func

        kwargs = _httpify(func)
        if kwargs:
            uri = uri or kwargs.get("uri")
            methods = methods or kwargs.get("methods")
            request = request or kwargs.get("request")
            response = response or kwargs.get("response")
            error = error or kwargs.get("error")
        if not uri:
            if hasattr(func, "__qualname__"):
                uri = func.__qualname__
            else:
                uri = func.__name__
            uri = format_uri(uri)
        if not methods:
            methods = ["GET"]
        elif isinstance(methods, str):
            methods = methods.split(",")

        methods = tuple(map(format_method, methods))

        func.__http_uri__ = uri or format_uri(func.__qualname__)
        func.__http_methods__ = methods
        func.__http_request__ = request
        func.__http_response__ = response
        func.__http_error__ = error
        return func

    wrap.__name__ = "http"
    if func is None:
        return wrap

    return wrap(func)


class Renders(object):
    def __init__(self, name):
        self._name = name
        self._render_dict = {}
        self.__alias = dict()

    def alias(self, name: str, alias: str):
        if name in self:
            raise ValueError("name {} already exist".format(name))
        self.__alias[name] = alias

    @property
    def name(self):
        return self._name

    @property
    def render_dict(self):
        return self._render_dict

    @property
    def render_default(self) -> Callable:
        return self._render_dict.get("default") or self.get_defalt_random()

    @render_default.setter
    def render_default(self, render):
        self.register("default", render)

    def register(self, name: str, render: Callable):
        if name in self.__alias:
            raise ValueError("name {} already exist".format(name))
        if name not in self._render_dict.values():
            if callable(render):
                self._render_dict[name] = render
            else:
                raise TypeError("render must be callable")
        else:
            raise ValueError("name {} already exist".format(name))

    def safe_register(self, name: str, render: Callable):
        if name not in self:
            self.register(name, render)

    def get(self, name: str):
        name = self.__alias.get(name, name)
        return self._render_dict[name]

    def get_defalt_random(self) -> Callable:
        if "default" in self._render_dict:
            raise ValueError("default render already set")
        for render in self._render_dict.values():
            self._render_dict["default"] = render
            return render
        raise ValueError("can not set random render with empty render_dict")

    def __len__(self):
        return len(self._render_dict)

    def __bool__(self):
        return bool(self._render_dict)

    def __contains__(self, item):
        return item in self._render_dict

    def __call__(self, name: str) -> Callable:
        def _wrap(func: Callable) -> Callable:
            self.register(name, func)
            return func

        return _wrap

    def init(self):
        pass


class RequestRender(Renders):
    def __init__(self):
        super().__init__("request")

    @staticmethod
    async def null(request: "Request") -> Dict:
        return dict()

    @staticmethod
    def set_trace(request: "Request"):
        headers = dict(request.headers)
        send_trace(headers)

    def init(self):
        self.safe_register("null", self.null)


class ResponseRender(Renders):
    def __init__(self):
        super().__init__("response")


class ErrorRender(Renders):
    def __init__(self):
        super().__init__("error")


def return_self(x: Any) -> Any:
    return x


REQUEST_RENDER = RequestRender()
RESPONSE_RENDER = ResponseRender()
ERROR_RENDER = ErrorRender()


def register(_type, func):
    if not isinstance(_type, type):
        # logger.warning(f"you register a non-type value of {_type} into TRANS_FUNC")
        ...
    if not callable(func):
        raise TypeError("func {} is not callable".format(func))
    _TRANS_FUNC_MAPPING[_type] = func


class BaseDrpcException(Exception):
    code: int = 500
    error_code: str = 100000
    message: str = "undefined error"


_TRANS_FUNC_MAPPING = {
    str: str,
    int: int,
    float: float,
    dict: dict,
    list: list,
    tuple: tuple,
    Dict: dict,
    List: list,
    Tuple: tuple,
    bool: bool,
    type(None): return_self,
    None: return_self,
    Any: return_self,
}


def trans_value(v: Any, _type: type) -> Any:
    if v is None and type(None) in _type.__args__:
        return v
    for __type in _type.__args__:
        try:
            return _TRANS_FUNC_MAPPING[__type](v)
        except Exception:
            continue
    raise NotImplementedError


def dataclass_format(x: Any) -> Dict:
    return x.__dict__


def parse_union(_type: type, mapping: Optional[Dict] = None) -> Callable:
    if mapping is None:
        mapping = _TRANS_FUNC_MAPPING
    for __type in _type.__args__:
        if mapping.get(__type, None) is None:
            if __type.__module__ == "typing" and __type.__origin__ == Union:
                mapping[__type] = parse_union(__type)
    mapping[_type] = partial(trans_value, _type=_type)
    return mapping[_type]


def get_trans_func(_type: type, mapping: Optional[Dict] = None) -> Callable:
    if mapping is None:
        mapping = _TRANS_FUNC_MAPPING
    if mapping.get(_type):
        return mapping[_type]
    elif _type.__module__ == "typing":
        if _type.__origin__ == Union:
            return parse_union(_type)
        else:
            register(_type, _type.__origin__)
            return _type.__origin__
            # raise NotImplementedError
    elif hasattr(_type, "__dataclass_fields__"):
        register(_type, dataclass_format)
        return dataclass_format
    else:
        return _type


class RequestParamLackError(BaseDrpcException):
    code = 208
    error_code = 100101
    message = "requests lack of param"


class RequestParamInvalidError(BaseDrpcException):
    code = 208
    error_code = 100102
    message = "requests params type error"


def gen_func_to_format_params(func: Callable) -> Callable:
    func.__annotations__.update(typing.get_type_hints(func))
    signature = inspect.signature(func)
    annotations = dict()
    parameters = set()
    not_default = set()
    check_invalid = True
    for name, sig in signature.parameters.items():
        parameters.add(name)
        if sig.kind.value == 3:
            continue
        if sig.kind.value == 4:
            check_invalid = False
            continue
        if sig.annotation != inspect._empty:
            annotations[name] = sig.annotation
        if sig.default == inspect._empty:
            not_default.add(name)
        else:
            if name not in annotations:
                annotations[name] = type(sig.default)
    trans = dict((k, get_trans_func(annotations[k])) for k in annotations)

    def format_func(kwargs: Dict) -> Dict:
        for key in not_default:
            if key not in kwargs:
                msg = f"field `{key}` must be assiged"
                raise RequestParamLackError(msg)
        if check_invalid:
            for key in kwargs:
                if key not in parameters:
                    msg = f"field named `{key}` is invalid"
                    raise RequestParamInvalidError(msg)

        for key in annotations:
            if key not in kwargs:
                continue
            val = kwargs[key]
            if not isinstance(val, str):
                continue
            try:
                kwargs[key] = trans[key](val)
            except Exception as e:
                msg = f"fail to convert value {val} to {annotations[key]}"
                logger.exception(e)
                raise RequestParamInvalidError(msg)
        return kwargs

    format_func.__name__ = f"{func.__name__}_format_params"
    return format_func


class WebRoutes(object):

    _methods_allow = ("GET", "POST", "DELETE", "PATCH", "PUT", "OPTIONS", "HAED")

    def __init__(self) -> None:
        super().__init__()
        self._routes = dict()

    def route(
        self,
        uri: str,
        methods: Union[Iterable[str], str] = "GET",
        request_render: Union[Callable, str] = "default",
        response_render: Union[Callable, str] = "default",
        error_render: Union[Callable, str] = "default",
    ):

        def wrap(func):
            self.add_route(func, uri, methods, request_render, response_render, error_render)
            return func

        return wrap

    def get(self, uri: str, *args, **kwargs):

        def wrap(func):
            self.add_route(func, uri, methods=("get",), *args, **kwargs)
            return func

        wrap.__name__ = "get"
        return wrap

    def post(self, uri: str, *args, **kwargs):
        def wrap(func):
            self.add_route(func, uri, methods=("post",), *args, **kwargs)
            return func

        wrap.__name__ = "post"
        return wrap

    def patch(self, uri: str, *args, **kwargs):

        def wrap(func):
            self.add_route(func, uri, methods=("patch",), *args, **kwargs)
            return func

        wrap.__name__ = "patch"
        return wrap

    def delete(self, uri: str, *args, **kwargs):

        def wrap(func):
            self.add_route(func, uri, methods=("delete",), *args, **kwargs)
            return func

        wrap.__name__ = "delete"
        return wrap

    def put(self, uri: str, *args, **kwargs):
        def wrap(func):
            self.add_route(func, uri, methods=("put",), *args, **kwargs)
            return func

        wrap.__name__ = "put"
        return wrap

    def head(self, uri: str, *args, **kwargs):

        def wrap(func):
            self.add_route(func, uri, methods=("head",), *args, **kwargs)
            return func

        wrap.__name__ = "head"
        return wrap

    def options(self, uri: str, *args, **kwargs):
        def wrap(func):
            self.add_route(func, uri, methods=("options",), *args, **kwargs)
            return func

        wrap.__name__ = "options"
        return wrap


class BaseHttpServer(BaseServer, WebRoutes):
    """Create web server from routes."""

    Request: "Request"
    Response: "Request"
    _routes: Dict
    _app = None

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.REQUEST_RENDER = kwargs.get("request_render", REQUEST_RENDER)
        self.RESPONSE_RENDER = kwargs.get("response_render", RESPONSE_RENDER)
        self.ERROR_RENDER = kwargs.get("error_render", ERROR_RENDER)
        self._http_enable = True
        uri_prefix: str = kwargs.get("uri_prefix") or ""
        if uri_prefix:
            uri_prefix = uri_prefix.strip("/")
            uri_prefix = "/" + uri_prefix
        self.__http_uri_prefix__ = uri_prefix

    def _add_route(
        self,
        uri: str,
        method: str,
        func: Callable,
        request_render: Optional[Union[Callable, str]] = None,
        response_render: Optional[Union[Callable, str]] = None,
        error_render: Optional[Union[Callable, str]] = None,
        http: Optional[Union[Callable, str]] = None,
    ) -> None:

        request_render = request_render or "default"
        response_render = response_render or "default"
        error_render = error_render or "default"
        http = http or "default"

        if isinstance(error_render, str):
            error_render = self.ERROR_RENDER.get(error_render)

        if not callable(http):
            format_params_func = gen_func_to_format_params(func)

            if isinstance(request_render, str):
                request_render = self.REQUEST_RENDER.get(request_render)
            if isinstance(response_render, str):
                response_render = self.RESPONSE_RENDER.get(response_render)

            if not asyncio.iscoroutinefunction(func):
                if self._executor_pools:
                    loop = asyncio.get_running_loop()
                    run_in_executor = loop.run_in_executor
                    executor_pools = self._executor_pools

                    async def http(request: Request) -> Response:
                        kwargs = await request_render(request)
                        kwargs = format_params_func(kwargs)
                        _func = partial(func, **kwargs)
                        ret = await run_in_executor(executor_pools, _func)
                        return response_render(ret)

                else:

                    async def http(request: Request) -> Response:
                        kwargs = await request_render(request)
                        kwargs = format_params_func(kwargs)
                        ret = func(**kwargs)
                        return response_render(ret)

            else:

                async def http(request: Request, **kwargs) -> Response:
                    _kwargs = await request_render(request)
                    _kwargs = format_params_func(_kwargs)
                    kwargs.update(_kwargs)
                    ret = await func(**kwargs)
                    return response_render(ret)

        set_trace = self.REQUEST_RENDER.set_trace

        async def handler(request: Request, **kwargs) -> Response:
            set_trace(request)
            try:
                return await http(request)
            except BaseException as e:
                return error_render(e)
            finally:
                TRACE.set(None)

        handler.__name__ = func.__name__
        handler.__doc__ = func.__doc__

        self._app_add_route(method=method, path=uri, handler=handler)
        if self.DEBUG:
            logger.debug("register uri: %s, method: %s, function: %s", uri, method, func)

    def _app_add_route(self):
        raise NotImplementedError

    def _set_default_render(self) -> None:
        self.REQUEST_RENDER.init()
        self.RESPONSE_RENDER.init()
        self.ERROR_RENDER.init()

    def http_register(self, service: Any, *, prefix: Optional[str] = "", **kwargs):
        """Register api from object instance and parse routes from function docstring.

        Args:
            server (Any): server object instance
            prefix (Optional[str], optional): uri prefix

        Raises:
            TypeError: raise TypeError if server is a type object
            ValueError: raise ValueError if prefix not start with /
        """
        if hasattr(service, "__http__"):
            if prefix:
                logger.warning("prefix invalid for method being httpified")
            return

        if service in self._drpc_methods:
            if prefix:
                logger.warning("prefix invalid for registering function")
            return

        service.__http__ = True

        prefix = prefix or self.__http_uri_prefix__

        if hasattr(service, "__http_uri_prefix__") and service.__http_uri_prefix__ is None:
            service.__http_uri_prefix__ = ""
        else:
            if not prefix and hasattr(service, "__http_uri_prefix__"):
                prefix = service.__http_uri_prefix__

            if prefix:
                prefix = prefix.strip("/")
                prefix = "/" + prefix
            service.__http_uri_prefix__ = prefix

    async def create_http_server(self, http: Optional[Dict] = None, **kwargs) -> None:
        for service in self._drpc_services:
            if hasattr(service, "__http__"):
                if service.__http__ is False:
                    continue
            else:
                service.__http__ = True

            if not hasattr(service, "__http_methods__"):
                if any(hasattr(i, "__http__") for i in service.__drpc_methods__):
                    methods = list()
                    for method in service.__drpc_methods__:
                        if hasattr(method, "__http__"):
                            if method.__http__ is False:
                                continue
                            methods.append(method)
                    service.__http_methods__ = methods
                else:
                    cls = service.__class__
                    for method in service.__drpc_methods__:
                        format_http(getattr(cls, method.__name__))
                    service.__http_methods__ = list(service.__drpc_methods__)
            uri_prefix = service.__http_uri_prefix__
            for method in service.__http_methods__:
                _http = method.__http__
                if hasattr(method, "__http_uri_prefix_disable__"):
                    uri = method.__http_uri__
                else:
                    uri = uri_prefix + method.__http_uri__
                _methods = method.__http_methods__
                request = method.__http_request__
                response = method.__http_response__
                error = method.__http_error__
                for _method in _methods:
                    self._add_route(uri, _method, method, request, response, error, _http)

    def add_route(
        self,
        func: Callable,
        uri: str,
        methods: Union[Iterable[str], str] = "GET",
        request_render: Union[Callable, str] = "default",
        response_render: Union[Callable, str] = "default",
        error_render: Union[Callable, str] = "default",
    ) -> None:
        """A method to register functions with uri and methods into routes.

        Args:
            func (Callable): a function to convert to hanlder
            uri (str): path of the URL
            methods (Union[Iterable[str], str], optional): http methods
            request_render (Union[Callable, str], optional): a function to parse request to kwargs
            response_render (Union[Callable, str], optional): a function to convert return to web response
            error_render (Union[Callable, str], optional): a function to handle error

        Raises:
            ValueError: raise ValueError when method not in methods allowed
            TypeError: raise TypeError when render is not callable
        """
        # warnings.warn(
        #     "route is deprecated, use drpc.http instead",
        #     DeprecationWarning
        # )
        if isinstance(methods, str):
            methods = (methods,)
        methods = list(map(str.upper, methods))

        for method in methods:
            if method not in self._methods_allow:
                raise ValueError("Method {} is not allow".format(method))

        format_http(
            func,
            uri=uri,
            methods=methods,
            request=request_render,
            response=response_render,
            error=error_render,
            http=True,
        )
        self.register(func)

    def http_register_v1(self, server: Any, *, prefix: str = "", **kwargs):
        """Register api from object instance and parse routes from function docstring.

        Args:
            server (Any): server object instance
            prefix (Optional[str], optional): uri prefix

        Raises:
            TypeError: raise TypeError if server is a type object
            ValueError: raise ValueError if prefix not start with /
        """
        if prefix:
            prefix = prefix.strip("/")
            prefix = "/" + prefix

        if isinstance(server, dict):
            for key, val in server.items():
                key = key.strip("/")
                key = "/".join((prefix, key))
                self.register(val, prefix=key)
            return

        if inspect.isfunction(server) or inspect.iscoroutinefunction(server):
            server = [server]

        elif inspect.isclass(server):
            try:
                server = server()
            except Exception:
                raise TypeError("can not register server with a class witch can not initialise automatically")

        if not isinstance(server, (list, tuple)):
            all_methods = dir(server)
            _server = list()
            for method in all_methods:
                if method.startswith("__"):
                    continue
                method = getattr(server, method)
                if not callable(method):
                    continue
                _server.append(method)
            server = _server

        for method in server:
            self._register_v1(method, prefix)

    def _register_v1(
        self,
        method: Callable,
        prefix,
    ):
        doc: str = method.__doc__
        if not doc:
            return
        for line in doc.splitlines():
            line = line.strip()
            if line.startswith("HTTP: /"):
                uri, *args = line[6:].split()
                methods, rrequest, rresponse, rerror, *_ = [*args, *((None,) * 4)]
                if methods is None:
                    methods = "GET"
                elif "," in methods:
                    methods = methods.split(",")
                rrequest = rrequest or "default"
                rresponse = rresponse or "default"
                rerror = rerror or "default"
                # method.__http__ = True
                self.add_route(method, uri, methods, rrequest, rresponse, rerror)
                break

    def _init_routes_v1(self) -> None:
        """Create the web handle function basic the function name."""
        for (uri, method), (func, *renders) in self._routes.items():
            self._add_route(uri, method, func, *renders)


def load_ssl_context(
    cert_file: str, pkey_file: Optional[str] = None, protocol: Optional[int] = None, **kwargs
) -> ssl.SSLContext:
    if protocol is None:
        protocol = ssl.PROTOCOL_TLS_SERVER

    ctx = ssl.SSLContext(protocol)
    ctx.load_cert_chain(cert_file, pkey_file, **kwargs)
    return ctx


def create_sock(
    host,
    port,
) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except Exception:
        sock.setsockopt(socket.SOL_SOCKET, 15, 1)
    sock.bind((host, port))
    sock.listen()
    return sock


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return JSON_TRANS_FUNC[type(obj)](obj)
        except KeyError:
            if hasattr(obj, "__dataclass_fields__"):
                JSON_TRANS_FUNC[type(object)] = trans_dataclass
                return trans_dataclass(obj)
            return json.JSONEncoder.default(self, obj)


dumps = partial(json.dumps, cls=JsonEncoder, ensure_ascii=False)


def trans_dataclass(obj):
    return obj.__dict__


def trans_bytes(obj: bytes):
    return str(obj, encoding="utf-8")


def trans_datetime(obj: datetime.datetime):
    return obj.strftime("%Y-%m-%d %H:%M:%S")


def trans_date(obj: datetime.date):
    return obj.strftime("%Y-%m-%d")


def trans_uuid(obj: UUID):
    return obj.hex


JSON_TRANS_FUNC = {
    bytes: trans_bytes,
    datetime.datetime: trans_datetime,
    datetime.date: trans_date,
}


json_response = partial(_json_response, dumps=dumps)
TRACE: ContextVar[Optional[Dict]] = ContextVar("request-trace")


def send_trace(trace: Dict):
    if "x-request-id" not in trace:
        trace["x-request-id"] = uuid4().hex
    trace["start-time"] = time()
    TRACE.set(trace)


def format_error_msg(error):
    sio = io.StringIO()
    traceback.print_exception(type(error), error, error.__traceback__, None, sio)
    msg = sio.getvalue()
    sio.close()
    return msg


class ContentInvalidError(BaseDrpcException):
    code = 208
    error_code = 100103
    message = "invalid value error"


class AiohttpServer(BaseHttpServer):
    def _init_app(self, *args, **kwargs) -> Application:
        self._app = Application(*args, **kwargs)
        # self._app_add_route = self._app.router.add_route
        return self._app

    def _app_add_route(self, method: str, path: str, handler: Callable):
        if "<" in path and ">" in path:
            path = path.replace("<", "{").replace(">", "}")
        self._app.router.add_route(method=method, path=path, handler=handler)

    def _set_default_render(self) -> None:
        super()._set_default_render()
        AioRequestRender._init(self.REQUEST_RENDER)
        AioResponseRender._init(self.RESPONSE_RENDER)
        AioErrorRender._init(self.ERROR_RENDER)

    async def create_http_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        sock: Optional[socket.socket] = None,
        app_config: Optional[Dict] = None,
        ssl: Optional[Union[ssl.SSLContext, Tuple[str]]] = None,
        http: Optional[Dict] = None,
        swagger: bool = False,
        session: bool = False,
    ):
        if http:
            return await self.create_http_server(**http, http=None)
        if self._app is None:
            app_config = app_config or dict()
            self._init_app(**app_config)
        self._set_default_render()
        # self._init_routes()
        await BaseHttpServer.create_http_server(self)
        app = self._app
        if asyncio.iscoroutine(app):
            app = await app  # type: ignore
        runner = AppRunner(app)
        await runner.setup()
        if sock is None:
            sock = create_sock(host, port)
        if isinstance(ssl, tuple):
            ssl = load_ssl_context(*ssl)
        scheme = "https" if ssl else "http"
        self.web = SockSite(runner, sock, ssl_context=ssl)
        await self.web.start()
        logger.info(f"start web server in {scheme}://{host}:{port}")


class AioRequestRender(RequestRender):
    @classmethod
    async def auto(cls, request: "Request") -> Dict:
        """Parse request to a key-value object."""
        kwargs = dict()
        kwargs.update(request.query)
        kwargs.update(request.match_info)
        content_type = request.content_type.lower()
        if "json" in content_type:
            _kwargs = await cls.json(request)
            kwargs.update(_kwargs)
        elif "form" in content_type:
            _kwargs = await cls.form(request)
            kwargs.update(_kwargs)
        return kwargs

    @staticmethod
    async def json(request: "Request") -> Dict:
        """Parse request with json content-type to a key-value object."""
        try:
            kwargs = await request.json()
        except json.JSONDecodeError as e:
            raise ContentInvalidError("Invalid json-string: {}".format(e.args[0]))
        return kwargs

    @staticmethod
    async def form(request: "Request") -> Dict:
        """Parse request with form content-type to a key-value object."""
        kwargs = dict()
        _kwargs = await request.post()
        for key, val in _kwargs.items():
            if isinstance(val, FileField):
                kwargs[key] = val.file.read()
            else:
                kwargs[key] = val
        return kwargs

    @staticmethod
    async def simple(request: "Request") -> Dict:
        """Parse request with form content-type to a key-value object."""
        kwargs = dict()
        kwargs.update(request.query)
        kwargs.update(request.match_info)
        return kwargs

    @staticmethod
    async def query(request: "Request") -> Dict:
        return dict(request.query)

    @staticmethod
    async def match(request: "Request") -> Dict:
        return dict(request.match_info)

    def init(self):
        self.safe_register("default", self.auto)
        self.safe_register("auto", self.auto)
        self.safe_register("json", self.json)
        self.safe_register("form", self.form)
        self.safe_register("simple", self.simple)
        self.safe_register("query", self.query)
        self.safe_register("match", self.match)
        super().init()

    def _init(self):
        self.safe_register("default", AioRequestRender.auto)
        self.safe_register("auto", AioRequestRender.auto)
        self.safe_register("json", AioRequestRender.json)
        self.safe_register("form", AioRequestRender.form)
        self.safe_register("simple", AioRequestRender.simple)
        self.safe_register("query", AioRequestRender.query)
        self.safe_register("match", AioRequestRender.match)


class AioResponseRender(ResponseRender):
    @staticmethod
    def all(ret: Any) -> Response:
        """Convert function returned to web response.

        This function is to change the value of target function returned
        to make it more restful.

        Args:
            ret (Any): value of the target function returned

        Returns:
            Response: a rest-like dict result
        """
        if ret is None:
            ret = {"status": "success"}
        elif isinstance(ret, (str, int, bytes, float)):
            ret = {"data": ret}
        ret = {"code": 0, "msg": "ok", "data": ret}
        return json_response(ret)

    def init(self):
        self.safe_register("default", self.all)
        super().init()

    def _init(self):
        self.safe_register("default", AioResponseRender.all)


class AioErrorRender(ErrorRender):
    @staticmethod
    def all(error: BaseException) -> Response:
        """Handle error and convert it to web response.

        This function is to deal with the probloms what to show for user
        when the target function can not be done properly and raise the
        exceptions. And to make it more restful, it would analysis the error
        and get some value from the error.

        Args:
            error (BaseException): the exception of the target function raise
        Returns:
            Response: a rest-like dict result with error info
        """
        if isinstance(error, BaseDrpcException):
            code = error.code
            error_code = error.error_code

            if error.args:
                msg = ",".join(error.args)
            else:
                msg = error.message
        else:
            code = 500
            # msg = traceback.format_tb(error.__traceback__)
            # msg = "\n".join(msg)
            msg = format_error_msg(error)
            error_code = BaseDrpcException.error_code
            logger.exception(error)
        ret = {"code": error_code, "msg": msg}
        return json_response(ret, status=code)

    def init(self):
        self.safe_register("default", self.all)
        super().init()

    def _init(self):
        self.safe_register("default", AioErrorRender.all)
