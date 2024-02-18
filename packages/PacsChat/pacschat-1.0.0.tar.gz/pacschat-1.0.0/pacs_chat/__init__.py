import logging

__version__ = "1.0.0"


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add the formatter to the console handler
    ch.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(ch)

    return logger
