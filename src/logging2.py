import yaml
import logging
import logging.config
"""
Config the logger for this whole project
- Log streamed to standard out is colored like a rainbow
- Log is also written to file: /tmp/spiff.log

Usage:

* In the entrypoint file:
from sss_utils import logging2
logger = logging2.getLogger(__name__)

* In other files, simply get logger without config:
import logging
logger = logging.getLogger(__name__)

"""

CONFIG = """
version: 1
disable_existing_loggers: False
formatters:
    simple:
        format: "%(asctime)s %(levelname)s %(pathname)s %(funcName)s() #%(lineno)d: %(message)s"

handlers:
    console:
        class: rainbow_logging_handler.RainbowLoggingHandler
        formatter: simple
        stream: ext://sys.stdout

    file_handler:
        class: logging.handlers.RotatingFileHandler
        formatter: simple
        filename: /tmp/app.log
        maxBytes: 104857600 # 100MB
        backupCount: 20
        encoding: utf8

root:
    level: DEBUG
    handlers: [console, file_handler]
"""

logging.config.dictConfig(yaml.safe_load(CONFIG))


def getLogger(name):
    return logging.getLogger(name)