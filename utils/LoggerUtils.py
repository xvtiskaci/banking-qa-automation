import logging
import logging.config
import os


class LoggerUtils:
    log_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'logger_config.conf'))
    if os.path.exists(log_config_path):
        logging.config.fileConfig(fname=log_config_path)
    else:
        print(f"Error: {log_config_path} doesn't exist.")

    @staticmethod
    def info(message):
        return logging.getLogger(__name__).info(message)

    @staticmethod
    def debug(message):
        return logging.getLogger(__name__).debug(message)

    @staticmethod
    def error(message):
        return logging.getLogger(__name__).error(message)
