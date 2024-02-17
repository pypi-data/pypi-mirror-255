import argparse
import asyncio
import curses

import _curses

from pacs_chat import __version__
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
    async def runner(stdscr: "_curses.window", host: str, port: int):
        stdscr.clear()
        my, mx = stdscr.getmaxyx()
        chat_window = ChatWindow(mx, my)
        input_window = InputWindow(mx, my)
        async with ChatClient(host, port, input_window, chat_window) as chat_client:
            await chat_client.run()
        stdscr.clear()

    args = cli_args()
    asyncio.run(curses.wrapper(runner, args.host, args.port))
    curses.endwin()
