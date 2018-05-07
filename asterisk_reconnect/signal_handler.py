import signal
import re
import sys

class signal_handler:
    def __init__(self, logger, as_reconnect):

        self.logger = logger
        self.as_reconnect = as_reconnect

    def signal_numtoname(self, num):
        name = []
        for key in signal.__dict__.keys():
            if re.match("(SIG(?!_)\w+)", key) and getattr(signal, key) == num:
                name.append(key)

        if len(name) == 1:
            return name[0]
        else:
            return str(num)

    # Set up the signal handler
    def handle_signal(self, _signal, _frame):

        reason = self.signal_numtoname(_signal)
        self.logger.info('asterisk_reconnect received %s, terminating', reason)
        self.as_reconnect.kill_received = True
        self.as_reconnect.thread.join()
        self.logger.info('Threads shutdown, exiting.')
        sys.exit(0)
