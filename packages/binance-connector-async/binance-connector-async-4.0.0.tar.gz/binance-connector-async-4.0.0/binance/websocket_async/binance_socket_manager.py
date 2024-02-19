"""
注意：回调函数中on_open 函数为同步函数，其他回调函数都为异步函数
"""
import asyncio
import inspect
from typing import Optional
import logging
import threading
from websocket import (
    ABNF,
    create_connection,
    WebSocketException,
    WebSocketConnectionClosedException,
)
from binance.lib.utils import parse_proxies


class BinanceSocketManager(threading.Thread):
    def __init__(
            self,
            stream_url,
            on_message=None,
            on_open=None,
            on_close=None,
            on_error=None,
            on_ping=None,
            on_pong=None,
            logger=None,
            proxies: Optional[dict] = None,
    ):
        """
        :param on_open: 同步函数
        :param 其他回调函数都为异步函数
        """
        # check if the on_message, on_close, on_error, on_ping, on_pong are async functions
        if on_message:
            # 判断on_message是否是异步函数
            if inspect.iscoroutinefunction(on_message) is False:
                raise ValueError("on_message must be an async function")
        if on_open:
            if inspect.iscoroutinefunction(on_open) is True:
                raise ValueError("on_open must be an coroutine function")
        if on_close:
            if inspect.iscoroutinefunction(on_close) is False:
                raise ValueError("on_close must be an async function")
        if on_error:
            if inspect.iscoroutinefunction(on_error) is False:
                raise ValueError("on_error must be an async function")
        if on_ping:
            if not inspect.iscoroutinefunction(on_ping) is False:
                raise ValueError("on_ping must be an async function")
        if on_pong:
            if not inspect.iscoroutinefunction(on_pong) is False:
                raise ValueError("on_pong must be an async function")

        threading.Thread.__init__(self)

        if not logger:
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.stream_url = stream_url
        self.on_message = on_message
        self.on_open = on_open
        self.on_close = on_close
        self.on_ping = on_ping
        self.on_pong = on_pong
        self.on_error = on_error
        self.proxies = proxies
        self._proxy_params = parse_proxies(proxies) if proxies else {}

        self.create_ws_connection()

    def create_ws_connection(self):
        self.logger.debug(
            f"Creating connection with WebSocket Server: {self.stream_url}, proxies: {self.proxies}",
        )
        self.ws = create_connection(self.stream_url, **self._proxy_params)
        self.logger.debug(
            f"WebSocket connection has been established: {self.stream_url}, proxies: {self.proxies}",
        )
        self._callback_同步(self.on_open)

    def run(self):
        asyncio.run(self.read_data())

    async def send_message(self, message):
        self.logger.debug("Sending message to Binance WebSocket Server: %s", message)
        self.ws.send(message)

    async def ping(self):
        self.ws.ping()

    async def read_data(self):
        data = ""
        while True:
            try:
                op_code, frame = self.ws.recv_data_frame(True)
            except WebSocketException as e:
                if isinstance(e, WebSocketConnectionClosedException):
                    self.logger.error("Lost websocket connection")
                else:
                    self.logger.error("Websocket exception: {}".format(e))
                raise e
            except Exception as e:
                self.logger.error("Exception in read_data: {}".format(e))
                raise e

            if op_code == ABNF.OPCODE_CLOSE:
                self.logger.warning(
                    "CLOSE frame received, closing websocket connection"
                )
                await self._callback(self.on_close)
                break
            elif op_code == ABNF.OPCODE_PING:
                await self._callback(self.on_ping, frame.data)
                self.ws.pong("")
                self.logger.debug("Received Ping; PONG frame sent back")
            elif op_code == ABNF.OPCODE_PONG:
                self.logger.debug("Received PONG frame")
                await self._callback(self.on_pong)
            else:
                data = frame.data
                if op_code == ABNF.OPCODE_TEXT:
                    data = data.decode("utf-8")
                await self._callback(self.on_message, data)

    def close(self):
        if not self.ws.connected:
            self.logger.warn("Websocket already closed")
        else:
            self.ws.send_close()
        return

    async def _callback(self, callback, *args):
        if callback:
            try:
                await callback(self, *args)
            except Exception as e:
                self.logger.error("Error from callback {}: {}".format(callback, e))
                if self.on_error:
                    await self.on_error(self, e)

    def _callback_同步(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                self.logger.error("Error from callback {}: {}".format(callback, e))
                if self.on_error:
                    self.on_error(self, e)
