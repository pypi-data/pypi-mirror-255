# PacsChat

A simple chat server written in Python using asyncio. It also includes a simple terminal client to connect to the server. The client is written in Python using the curses library.

## Installation

To install PacsChat, you need to have Python 3.10 or higher. You can install it using pip:

```bash
pip install PacsChat
```

##  Usage

To start the server, you can use the following command:

```bash
pacs-chat-server [options]
```
Available options:
- `-h`, `--help`: Show help message and exit
- `-v`, `--version`: Show version and exit
- `-p`, `--port`: The port to listen on (default: 8081)
- `-n`, `--history`: The number of messages to keep in the history (default: 10)


After starting the server, you can connect to the server by entering the server's IP address and port number.

```bash
pacs-chat-client [options]
```

Available options:
- `-h`, `--help`: Show help message and exit
- `-v`, `--version`: Show version and exit
- `-s`, `--server`: The server's IP address (default: localhost)
- `-p`, `--port`: The server's port number (default: 8081)
