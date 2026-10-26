from selenium.webdriver import Keys

from elements.element import Element
from utils.LoggerUtils import LoggerUtils


class Input(Element):
    def __init__(self, by, locator, name):
        super().__init__(by, locator, name)

    def send_text(self, value):
        LoggerUtils.info("sent text to element: {}".format(self.name))
        self.find_element().send_keys(value)

    def clear_and_fill(self, value):
        LoggerUtils.info("clear and fill element: {}".format(self.name))
        element = self.find_element()  # ნუ გამოვიყენებთ ყოველთვის By.XPATH-ს.
        element.clear()
        element.send_keys(value)

    def upload_image(self, path):
        return self.find_element().send_keys(path)

    def press_enter(self):
        return self.find_element().send_keys(Keys.ENTER)
