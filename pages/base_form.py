from elements.element import Element
from utils.DriverUtils import DriverUtils


class BaseForm:

    def __init__(self, by, locator, name):
        self.element = Element(by, locator, name)

    def is_visible(self):
        locator = self.element.by, self.element.locator
        DriverUtils.wait_for_visible(locator)
        return self.element.is_visible()
