import logging
import datetime
import sys

def get_filename():
    if sys.platform == 'linux' or sys.platform == 'darwin':
        filename = "logs" + "/" + str(datetime.datetime.now().strftime("%Y")) + "/" +\
                               str(datetime.datetime.now().strftime("%m")) + "/" + "print_queue_info.log"
    else:
        filename = "logs" + "\\" + str(datetime.datetime.now().strftime("%Y")) + "\\" +\
                               str(datetime.datetime.now().strftime("%m")) + "\\" + "print_queue_info.log"
    return filename

logging_config = dict(
    version=1,
    formatters={
        'simple': {'format':
              '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
    handlers={
        'h': {"encoding": "utf8",
               "level": "DEBUG",
               "when": "midnight",
               "filename": get_filename(),
               "formatter": "simple",
               "class": "logging.handlers.TimedRotatingFileHandler"}
        },

    loggers={
        'root': {'handlers': ['h'],
                 'level': logging.DEBUG}
        }
)