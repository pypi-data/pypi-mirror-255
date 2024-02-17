from typing import Self, Union

from PersonalLibrary.Initial import importModule, Logger
from PersonalLibrary.Text.Text import Text

if importModule("PIL", "pystray"):
    from PIL import Image
    import pystray
    from pystray import *

    Logger.hide_log()


class EasySystemTray:
    def __init__(self, appName: str | Text, iconPath: str | Text = None, showName: str | Text = None) -> None:
        self.iconPath = iconPath = iconPath or r"./resource/assets/icon/icon.png"
        Logger.getLogger("EasySystemTray")
        self.iconImage = Image.open(self.iconPath)
        self.menuDict: dict[str, MenuItem] = dict()
        self.iconName = iconPath.split("/")[-1].split('.')[0]
        self.appName = appName
        self.Icon: pystray.Icon = pystray.Icon
        self.showName = showName or self.appName

    def BuildMenu(self,
                  text: str | Text,
                  action: callable,
                  menuName: str | Text = None,
                  default: bool = False,
                  enable: Union[bool, callable] = True,
                  checked: Union[bool, callable] = None,
                  visible: Union[bool, callable] = None,
                  *args,
                  **options) -> Self | None:
        """
        构建菜单
        :param menuName: 选项名称，默认和text一样
        :param text: 选项文本
        :param action:  点击选项后运行的函数
        :param default: 设置菜单项是否被选中为默认项。默认为 False。
        :param enable: 设置菜单项是否可用。可以传入一个布尔值或可调用对象，用于动态确定菜单项是否可用。
        :param checked: 设置菜单项是否被选中。可以传入一个布尔值或可调用对象，用于动态确定菜单项是否被选中。
        :param visible: 设置菜单项是否可见。可以传入一个布尔值或可调用对象，用于动态确定菜单项是否可见。
        :return: Self
        """
        if menuName is None:
            menuName = text

        if menuName not in self.menuDict:
            self.menuDict[menuName] = MenuItem(text, action, default, enable, checked, visible, *args, **options)
            return self
        else:
            Logger.warning(Text().translate("warning.tray.menu_name_already_exists").formatted(menuName))
            return None

    def getMenu(self, menuName: str):
        return self.menuDict[menuName]

    def start(self):
        menus = (menu for menu in list(self.menuDict.values()))
        Logger.info(Text().translate("info.tray.menu_start"))
        self.Icon(self.iconName, self.iconImage, self.showName, menus)

    def stop(self):
        self.Icon.stop()
