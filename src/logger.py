import logging
import time
import os


def configure_logging():
    # Not using resource_path here, because I want it to be seen outside the executable
    if not os.path.exists("./mcIVASMAKER_logs"):
        os.makedirs("./mcIVASMAKER_logs")
    logging.basicConfig(
        filename=f"./mcIVASMAKER_logs/Log{time.strftime('%y_%m_%d-%H_%M_%S', time.localtime())}.log",
        format="{asctime:s}::{name:s}_[{levelname:^8s}] - {message:s}",
        datefmt='%Y/%m/%d %I:%M:%S%p',
        style='{',
        encoding='utf-8',
        level=logging.DEBUG
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "{asctime:s}::{name:s}_[{levelname:^8s}] - {message:s}",
        style="{",
        datefmt='%Y/%m/%d %I:%M:%S%p'
    ))
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

