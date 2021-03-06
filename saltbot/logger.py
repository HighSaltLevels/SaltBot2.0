""" Logging Module """


class Logger:
    """ Logger object for writing the log file """

    def __init__(self, logfile="log.txt"):
        self._logfile = logfile
        self._initialize_logfile()

    def log_sent(self, author, channel, msg):
        """ Log a message sent event """
        print(f"{author} in {channel} <- {msg}\n")
        with open(self._logfile, "a") as stream:
            stream.write(f"{author} in {channel} <- {msg}\n")

    def log_received(self, author, channel, msg):
        """ Log a message received event """
        print(f"{author} from {channel} -> {msg}")
        with open(self._logfile, "a") as stream:
            stream.write(f"{author} from {channel} -> {msg}\n")

    def log(self, msg):
        """ Print the message and write to the log file """
        print(msg)
        with open(self._logfile, "a") as stream:
            stream.write(f"{msg}\n")

    def _initialize_logfile(self):
        """ Clear the log file """
        with open(self._logfile, "w"):
            pass
