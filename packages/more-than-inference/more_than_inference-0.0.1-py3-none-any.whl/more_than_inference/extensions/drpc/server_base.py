from loguru import logger

from more_than_inference.extensions.drpc.pack import AiohttpServer as HttpServer


class DrpcServer:
    CLIENT_MAX_SZIE = 104857600  # config the request body to size 100MB (1024*1024*100)
    def _callback_func(i): return i
    def __init__(self, port): self.port = port

    async def probe(self):
        """Health check.
        HTTP: /probe GET,POST

        Returns:
            Empty: nothing to return
        """
        return

    async def start(self, message: bytes):
        """
        HTTP: /start POST,GET
        """
        return self.__callback_func(message)

    def run(self):
        _port = self.port
        _run_args = dict(
            port=_port,
            app_config=dict(
                client_max_size=self.CLIENT_MAX_SZIE
            )
        )
        logger.info(f"DRPC_SERVICE LISTEN: `0.0.0.0:{_port}`")
        logger.info(f"DRPC_SERVICE ARGS: {_run_args}")
        server = HttpServer()
        server.register(self)
        server.run(**_run_args)
