import os, time, logging, multiprocessing
from logging.handlers import QueueHandler

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'ProcessNo.0': '\033[94m',  # Light Green
        'ProcessNo.1': '\033[95m',   # Light Cyan
        'ProcessNo.2': '\033[96m',   # Light Blue
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'RESET': '\033[0m'    # Reset
    }
    def format(self, record):
        color = self.COLORS.get(record.processName, self.COLORS['RESET'])
        if record.levelname == "WARNING" or record.levelname == "ERROR":
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        message = super().format(record)
        return f'{color}{message}{self.COLORS["RESET"]}'

loglevels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        }

def initCentralLogger(queue, rundir, loglevel):
    root = logging.getLogger()

    console_formatter = ColoredFormatter('%(processName)-11s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(loglevels[loglevel])
    root.addHandler(console_handler)

    file_formatter = logging.Formatter('%(asctime)s %(processName)-11s %(module)-18s %(levelname)-7s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    folder_path = os.path.join(rundir, "logs")
    os.makedirs(folder_path, exist_ok = True)
    file_handler = logging.FileHandler(os.path.join(folder_path, "vectormpp.log"))
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    root.addHandler(file_handler)

    root.setLevel(logging.DEBUG)
    root.debug(f"{multiprocessing.current_process().name} starts.")
    while True:
        while not queue.empty():
            record = queue.get()
            if record is None:
                root.debug(f"{multiprocessing.current_process().name} ends.")
                return
            logging.getLogger(record.name).handle(record)
        time.sleep(1)

def initWorkerLogger(queue, loglevel):
    root = logging.getLogger()
    if not any(isinstance(handler, QueueHandler) for handler in root.handlers):
        root.addHandler(QueueHandler(queue))
    root.setLevel(loglevels[loglevel])

    pyhelm3 = logging.getLogger('pyhelm3.command')
    pyhelm3.setLevel(logging.INFO)
