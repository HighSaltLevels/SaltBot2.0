class Logger(object):
    def __init__(self, logfile="log.txt"):
        self._logfile = logfile
        self._initialize_logfile()

    def log_sent(self, author, channel, msg):
        print(f"{author} in {channel} <- {msg}")
        with open(self._logfile, "a") as stream:
            stream.write(f"{author} in {channel} <- {msg}\n")

    def log_received(self, author, channel, msg):
        print(f"{author} from {channel} -> {msg}")
        with open(self._logfile, "a") as stream:
            stream.write(f"{author} from {channel} -> {msg}\n")

    def _initialize_logfile(self):
        with open(self._logfile, "w"):
            pass
