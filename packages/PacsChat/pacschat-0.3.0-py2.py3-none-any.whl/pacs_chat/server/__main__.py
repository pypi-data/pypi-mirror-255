import argparse
import asyncio

from pacs_chat import __version__
from pacs_chat.server.handler import RequestHandler


def cli_args():
    parser = argparse.ArgumentParser(
        description="chatter-py:A simple chat server written in Python using asyncio and tcp sockets."
    )

    # Add version argument
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s v{__version__}"
    )

    # Add ports argument

    parser.add_argument(
        "--port", "-p", type=int, default=8081, help="Port to run the server on"
    )

    # Number of recent messages to store
    parser.add_argument(
        "--history",
        "-n",
        type=int,
        default=10,
        help="Number of recent messages to store",
    )

    args = parser.parse_args()
    return args


def main():
    async def run_server():
        args = cli_args()
        handler = RequestHandler(args.history)

        srv = await asyncio.start_server(handler.callback, "0.0.0.0", args.port)
        try:
            await srv.serve_forever()

        except asyncio.CancelledError:
            print("Server stopped")

        except Exception as e:
            print(f"Exception occurred: {e}")

        finally:
            srv.close()
            await srv.wait_closed()

    with asyncio.Runner() as runner:
        runner.run(run_server())


if __name__ == "__main__":
    main()
