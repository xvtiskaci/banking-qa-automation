from elements.element import Element


class TextField(Element):

    def __init__(self, by, locator, name):
        super().__init__(by, locator, name)