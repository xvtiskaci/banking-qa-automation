
from selenium.webdriver import ActionChains

from elements.element import Element
from managers.DriverManager import DriverManager


class Slider(Element):
    def __init__(self, by, locator, name):
        super().__init__(by, locator, name)

    def click_and_hold(self):
        actions = ActionChains(DriverManager.get_driver())
        actions.click_and_hold(self.find_element()).perform()

    def move_slider(self):
        actions = ActionChains(DriverManager.get_driver())
        actions.move_to_element(self.find_element()).perform()
