import json
import logging
import logging.handlers
from pathlib import Path

# Text comment to check if development mode is working.

# For a list of the logger variables used in this module, see: https://docs.python.org/3/library/logging.html


logs_path = Path.home() / 'logs'
if not Path.exists(logs_path):
    Path.mkdir(logs_path)

local_logger_file = logs_path / 'local_logger.log'
if not Path.exists(local_logger_file):
    local_logger_file.touch()

local_logger = logging.getLogger("libs.logging.local_logger")


def local_logger_config():
    local_logger.setLevel(logging.INFO)
    log_handler = logging.FileHandler(local_logger_file.as_posix())
    log_format = (
        '{ "loggerName":"%(name)s", "timestamp":"%(asctime)s", '
        '"pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", '
        '"filename":"%(filename)s", "functionName":"%(funcName)s", '
        '"levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", '
        '"levelName":"%(levelname)s", "message":"%(message)s"}'
    )
    log_handler.setFormatter(logging.Formatter(log_format))
    local_logger.addHandler(log_handler)


local_logger_config()


system_logger = logging.getLogger("libs.logging.system_logger")


def system_logger_config():
    system_logger.setLevel(logging.INFO)
    log_handler = logging.handlers.SysLogHandler('/dev/log')
    log_format = (
        '{"loggerName":"%(name)s", "timestamp":"%(asctime)s", '
        '"pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", '
        '"filename":"%(filename)s", "functionName":"%(funcName)s", '
        '"levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", '
        '"levelName":"%(levelname)s", "message":"%(message)s"}'
    )
    log_handler.setFormatter(logging.Formatter(log_format))
    system_logger.addHandler(log_handler)


system_logger_config()


"""
NB system_logger (which uses the default settings for SysLogHandler) sends all logs to a UNIX socket at /dev/log; syslogd listens on that socket and then does with those logs whatever it's told to in /etc/syslog.conf.  Under the default configuration, these logs can be read from the command line using journalctl; example follows: "journalctl | less | grep python | grep CRITICAL"
"""
