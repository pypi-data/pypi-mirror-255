import argparse
import asyncio
import curses

import _curses
from venv import logger

from pacs_chat import __version__, setup_logger
from pacs_chat.client.chat_client import ChatClient
from pacs_chat.client.curses_gui import ChatWindow, InputWindow


def cli_args():
    parser = argparse.ArgumentParser(
        description="chatter-py-client:A simple chat client written in Python using asyncio and tcp sockets. It is meant to be only \
            used against chatter-py server."
    )

    # Add version argument
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s v{__version__}"
    )

    # Add ports argument
    parser.add_argument(
        "--port", "-p", type=int, default=8081, help="server port to connect to"
    )

    # Add host address argument
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="server address to connect to",
    )

    args = parser.parse_args()
    return args


def main():
    logger = setup_logger(__name__)

    async def runner(stdscr: "_curses.window", host: str, port: int):
        try:
            my, mx = stdscr.getmaxyx()
            chat_window = ChatWindow(mx, my)
            input_window = InputWindow(mx, my)
            async with ChatClient(host, port, input_window, chat_window) as chat_client:
                await chat_client.run()
            stdscr.erase()
            curses.endwin()

        except ConnectionRefusedError:
            logger.error(
                f"Connection refused by server, please check the server address and port"
            )

        except Exception as e:
            logger.error(f"an unknown error happened, details{e.__repr__()}")

    args = cli_args()
    asyncio.run(curses.wrapper(runner, args.host, args.port))
