def clearColor():
    return Colors.RESET


class Colors(str):
    # 文本颜色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # 背景颜色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'

    # 重置所有样式
    RESET = '\033[0m'

    def __str__(self):
        return ""


def printColor(colorName: str):
    print(Colors.__dict__[colorName.upper()] + "Hello World!" + Colors.RESET)


def setColor(colorName: str, colorValue: str):
    Colors.__dict__[colorName.upper()] = colorValue


def getColor(colorName: str):
    return Colors.__dict__[colorName.upper()]


def addColor(colorName: str, colorValue: str):
    Colors.__dict__[colorName.upper()] = colorValue
