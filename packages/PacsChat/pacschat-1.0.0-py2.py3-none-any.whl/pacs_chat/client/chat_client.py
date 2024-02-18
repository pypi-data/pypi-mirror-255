import asyncio
import concurrent.futures
from typing import Protocol

from pacs_chat import setup_logger


class InputWindow(Protocol):
    def refresh(self) -> None: ...

    def get_input_message(self) -> bytes: ...


class ChatWindow(Protocol):
    def add_message(self, message: str): ...


class ChatClient:
    def __init__(
        self, addr: str, port: int, input_window: InputWindow, chat_window: ChatWindow
    ) -> None:
        self.addr = addr
        self.port = port
        self.chat_window = chat_window
        self.input_window = input_window
        self.stop_signal = asyncio.Event()
        self.logger = setup_logger(__name__)

    async def __aenter__(self):
        self.reader, self.writer = await asyncio.open_connection(self.addr, self.port)
        name = input((await self.reader.read(100)).decode())

        self.writer.write(name.encode())
        await self.writer.drain()

        num_messages = int((await self.reader.readline()).decode())
        for _ in range(num_messages):
            self.chat_window.add_message((await self.reader.readline()).decode())

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def run(self):
        async def input_handler():
            while not self.stop_signal.is_set():
                self.input_window.refresh()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    message = await asyncio.get_event_loop().run_in_executor(
                        executor, self.input_window.get_input_message
                    )
                    if not (len(message) == 0 or message == b"\n"):
                        self.writer.write(message)
                        await self.writer.drain()

        async def incoming_message_handler():
            while not self.stop_signal.is_set():
                if message := (await self.reader.readline()).decode():
                    self.chat_window.add_message(message)
                else:
                    self.logger.warn(
                        "Server closed the connection, press 'enter' key to exit."
                    )
                    self.stop_signal.set()
                    break

        await asyncio.gather(input_handler(), incoming_message_handler())
