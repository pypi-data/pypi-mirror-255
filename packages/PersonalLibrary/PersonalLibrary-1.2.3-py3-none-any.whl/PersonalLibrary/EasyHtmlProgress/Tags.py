class Tags:
    # 元素
    HREF = "href"
    CLASS = "class"
    INPUT = "input"
    NAME = "name"
    VALUE = "value"
    STYLE = "style"
    SRC = "src"
    TITLE = "title"
    ID = "id"
    TYPE = "type"
    ALT = "alt"

    # 标签
    DIV = "div"
    P = "p"
    A = "a"
    SPAN = "span"
    BUTTON = "button"
    IMG = "img"
    BR = "br"
    SCRIPT = "script"

    def getElements(self) -> list:
        return [self.HREF, self.CLASS, self.INPUT, self.NAME, self.VALUE, self.STYLE, self.SRC, self.TITLE, self.ID,
                self.TYPE, self.ALT]

    def getTags(self) -> list:
        return [self.DIV, self.P, self.A, self.SPAN, self.BUTTON, self.IMG, self.SCRIPT]

    def isTag(self, tag: str) -> bool:
        return tag in self.getTags()

    def hasTag(self, tag: str) -> bool:
        return tag in self.getTags()

    def isElement(self, element: str) -> bool:
        return element in self.getElements()

    def hasElement(self, element: str) -> bool:
        return element in self.getElements()
