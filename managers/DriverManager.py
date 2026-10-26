import threading

from metas.SingletonMeta import Singleton
from managers.BrowserFactory import BrowserFactory


class DriverManager(metaclass=Singleton):
    __driver = None
    __lock = threading.Lock()

    @classmethod
    def get_driver(cls, browser="chrome"):
        if cls.__driver is None:
            with cls.__lock:
                if cls.__driver is None:
                    cls.__driver = BrowserFactory.get_browser(browser)
        return cls.__driver

    @classmethod
    def get_active_driver(cls):
        return cls.__driver

    @classmethod
    def close_driver(cls):
        if cls.__driver is not None:
            with cls.__lock:
                if cls.__driver is not None:
                    cls.__driver.quit()
                    cls.__driver = None
