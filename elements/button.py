from elements.element import Element


class Button(Element):
    def __init__(self, by, locator, name):
        super().__init__(by, locator, name)
