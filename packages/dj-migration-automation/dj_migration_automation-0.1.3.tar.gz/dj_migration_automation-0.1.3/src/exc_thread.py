import threading
import logging


# get the logger for the pack from global configuration file logging.json
logger = logging.getLogger("root")


class ExcThread(threading.Thread):
    """LogThread should always e used in preference to threading.Thread.

    The interface provided by LogThread is identical to that of threading.Thread,
    however, if an exception occurs in the thread the error will be logged
    (using logging.exception) rather than printed to stderr.

    This is important in daemon style applications where stderr is redirected
    to /dev/null.

    """
    def __init__(self,  exc_list, **kwargs):
        super(ExcThread, self).__init__(**kwargs)
        self._real_run = self.run
        self.run = self._wrap_run
        self.exc_list = exc_list

    def _wrap_run(self):
        try:
            self._real_run()
        except Exception as ex:
            logger.error(ex, exc_info=True)
            self.exc_list.append({self.name: ex})
