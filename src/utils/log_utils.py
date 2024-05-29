import logging
import logging.handlers
import os
import time

from utils.folder_utils import FolderUtils


class LogUtils:
    def __init__(self):
        FolderUtils().create_file("../reports/log", "log.log")
        self.handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "../reports/log/log.log"))
        self.formatter = logging.Formatter(logging.BASIC_FORMAT)
        self.root = logging.getLogger("Report")

    def start(self):
        self.handler.setFormatter(self.formatter)
        self.root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        self.root.addHandler(self.handler)
        self.root.info("Logging started")

    def stop(self):
        self.root.info("Logging stopped")
        self.root.removeHandler(self.handler)
        self.handler.close()

    def log_debug(self, message):
        self.root.debug(message)

    def log_info(self, message):
        self.root.info(message)

    def log_warning(self, message):
        self.root.warning(message)

    def log_error(self, message):
        self.root.error(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

    def log_critical(self, message):
        self.root.critical(message)