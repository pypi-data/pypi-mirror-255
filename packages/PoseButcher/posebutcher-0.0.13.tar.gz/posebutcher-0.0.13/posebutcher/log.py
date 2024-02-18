
import logging
import mcol

logger = logging.getLogger('PoseButcher')

import haggis.logs

haggis.logs.add_logging_level('HEADER',logging.INFO+2)
haggis.logs.add_logging_level('SUCCESS',logging.INFO+1)
haggis.logs.add_logging_level('OUT',logging.INFO+2)

class WarningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno == logging.WARNING
    
class InfoFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno == logging.INFO
    
class ErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno >= logging.ERROR
    
class DebugFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno == logging.DEBUG

LOG_CONFIG = {
  "version": 1,
  "disable_existing_loggers": False,
  "formatters": {
    "green": { "format": f"{mcol.inverse}{mcol.bold}{mcol.green} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    "red": { "format": f"{mcol.inverse}{mcol.bold}{mcol.red} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    "yellow": { "format": f"{mcol.inverse}{mcol.bold}{mcol.yellow} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    "blue": { "format": f"{mcol.inverse}{mcol.bold}{mcol.lilac} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    "green": { "format": f"{mcol.inverse}{mcol.bold}{mcol.green} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    "red": { "format": f"{mcol.inverse}{mcol.bold}{mcol.red} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    "yellow": { "format": f"{mcol.inverse}{mcol.bold}{mcol.yellow} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    "blue": { "format": f"{mcol.inverse}{mcol.bold}{mcol.lilac} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    # "green": { "format": f"{mcol.inverse}{mcol.bold} PoseButcher {mcol.green} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    # "red": { "format": f"{mcol.inverse}{mcol.bold} PoseButcher {mcol.red} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    # "yellow": { "format": f"{mcol.inverse}{mcol.bold} PoseButcher {mcol.yellow} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
    # "blue": { "format": f"{mcol.inverse}{mcol.bold} PoseButcher {mcol.lilac} %(levelname)s {mcol.clear} %(message)s{mcol.clear}"},
  },
  "filters": {
    "warning": {
      "()": WarningFilter
    },
  "info": {
      "()": InfoFilter
    },
    "error": {
      "()": ErrorFilter
    },
    "debug": {
      "()": DebugFilter
    }
  },
  "handlers": {
    "debug": {
      "class": "logging.StreamHandler",
      "formatter": "blue",
      "stream": "ext://sys.stdout",
      "filters": [ "debug" ],
    },
    "info": {
      "class": "logging.StreamHandler",
      "formatter": "green",
      "stream": "ext://sys.stdout",
      "filters": [ "info" ],
    },
    "warning": {
      "class": "logging.StreamHandler",
      "formatter": "yellow",
      "stream": "ext://sys.stdout",
      "filters": [ "warning" ],
    },
    "error": {
      "class": "logging.StreamHandler",
      "formatter": "red",
      "stream": "ext://sys.stdout",
      "filters": [ "error" ],
    },
  },
  "loggers": {
    "root": {
      "level": "DEBUG", 
      "handlers": [ "info", "warning", "error", "debug" ]
    }
  }
}

# import sys
# import os

# class HiddenPrints:
#     def __enter__(self):
#         self._original_stdout = sys.stdout
#         sys.stdout = open(os.devnull, 'w')

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         sys.stdout.close()
#         sys.stdout = self._original_stdout

