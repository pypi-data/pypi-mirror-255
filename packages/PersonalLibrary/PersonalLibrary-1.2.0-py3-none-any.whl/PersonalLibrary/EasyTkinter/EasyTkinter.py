from functools import wraps
from tkinter import *
from typing import Any, Self

import _tkinter

from PersonalLibrary.EasyTkinter.CanvasFunction import CanvasFunction

try:
    from Controllers import Controllers
except ImportError:
    from PersonalLibrary.EasyTkinter.Controllers import Controllers

from PersonalLibrary.Initial import Logger, importModule
from PersonalLibrary.Text.Text import Text

if importModule("PIL"):
    from PIL import Image, ImageTk


class EasyTkinter:
    def __init__(self, title: str = 'tkinter GUI', size: tuple = (400, 300),
                 resizable: tuple[bool] = (False, False)) -> None:
        Logger.getLogger('EasyTkinter')
        self.root = Tk()
        self.root.title(title)
        self.root.geometry(f"{size[0]}x{size[1]}")
        self.root.resizable(resizable[0], resizable[1])

        self.menuDict: dict[str, Menu] = dict()
        self.labelDict: dict[str, Label] = dict()
        self.textDict: dict[str, Text] = dict()
        self.buttonDict: dict[str, Button] = dict()
        self.entryDict: dict[str, Entry] = dict()
        self.canvasDict: dict[str, Canvas] = dict()
        self.labelFrameDict: dict[str, LabelFrame] = dict()
        self.checkbuttonDict: dict[str, Checkbutton] = dict()
        self.radiobuttonDict: dict[str, Radiobutton] = dict()

        self.supportController: dict = {
            "label": self.labelDict,
            "text": self.textDict,
            "button": self.buttonDict,
            "labelframe": self.labelFrameDict,
            "entry": self.entryDict,
            "checkbutton": self.checkbuttonDict,
            "radiobutton": self.radiobuttonDict,
            "menu": self.menuDict,
            "canvas": self.canvasDict
        }

        self.Controller: dict = {
            "label": Label,
            "text": Text,
            "button": Button,
            "labelframe": LabelFrame,
            "entry": Entry,
            "checkbutton": Checkbutton,
            "radiobutton": Radiobutton,
            "menu": Menu,
        }

        self.controllerFuncDict: dict = dict()
        self._PhotoImage = None

    def getRoot(self) -> Tk:
        return self.root

    @Logger.ShowLog
    def start(self, n: int = 0) -> None:
        Logger.info(Text().translate("info.tkinter.show"))
        self.root.mainloop(n)

    def stop(self) -> None:
        self.root.quit()

    def destroy(self) -> None:
        self.root.destroy()

    def show(self) -> None:
        self.root.deiconify()

    def hide(self) -> None:
        self.root.withdraw()

    def setIcon(self, path: str) -> None:
        self.root.iconbitmap(path)

    @Logger.ShowLog
    def BuildController(self,
                        controllerName: str,
                        controller: Controllers | str,
                        master: Tk | Toplevel | LabelFrame = None,
                        **options):
        if master is None:
            master = self.root
        if controller not in self.supportController:
            Logger.error(
                Text().translate("error.tkinter.controller_not_supported").formatted(controller,
                                                                                     list(self.supportController.keys())
                                                                                     )
            )
            return None
        if not self._matchControllerName(controllerName):
            self.supportController[controller][controllerName] = self.Controller[controller](master, **options)
        else:
            Logger.error(
                Text().translate("error.tkinter.controller_already_exist").formatted(controllerName, controller))
        return self

    def getController(self, controllerName: str, controller: Controllers | str) -> Any:
        try:
            return self.supportController[controller][controllerName]
        except KeyError:
            return None

    def SetControllerGrid(self, controllerName: str, controller: Controllers | str, row: int, column: int,
                          **gridOptions) -> None:
        self.getController(controllerName, controller).grid(row=row, column=column, **gridOptions)

    def SetControllerPack(self, controllerName: str, controller: Controllers | str, **packOptions) -> None:
        self.getController(controllerName, controller).pack(**packOptions)

    def controllerFunction(self, controllerName: str, controller: Controllers | str, *args, **kwargs):
        """
        装饰器，用于可调用按钮的添加
        :param controller: 控件
        :param controllerName: 控件名称
        :return:
        """

        def decorator(func):
            self.controllerFuncDict[controllerName] = func

            @wraps(func)
            def wrapper(*TArgs, **TKwargs):
                if self._matchControllerName(controllerName):
                    lambdaCommand = lambda: self.controllerFuncDict[controllerName](*TArgs, **TKwargs)
                    self.supportController[controller][controllerName].config(command=lambdaCommand)
                else:
                    Logger.error(
                        Text().translate("error.tkinter.controller_not_build").formatted(controllerName, controller))

            wrapper(*args, **kwargs)
            return wrapper

        return decorator

    def _matchControllerName(self, controllerName: str):
        tmpDict = {}
        for controller in self.supportController.values():
            tmpDict.update(controller)
        return controllerName in tmpDict

    def configController(self, controllerName: str, controller: Controllers, **TKwargs):
        try:
            self.supportController[controller][controllerName].config(**TKwargs)
        except _tkinter.TclError as e:
            Logger.error(Text().translate("error.tkinter.unknown_option").formatted(e.__str__().split('option')[1]))
            return None

    def toImage(self, imagePath: str, size: tuple[int, int] = None):
        try:
            image = Image.open(imagePath)
            if size is not None:
                image = image.resize(size)
            self._PhotoImage = ImageTk.PhotoImage(image=image)
            return self._PhotoImage
        except FileNotFoundError:
            Logger.error(Text().translate("error.tkinter.image_not_found").formatted(imagePath))
            return None

    def BuildCanvas(self, canvasName: str, canvasFunction: CanvasFunction, **TKwargs):
        ...


if __name__ == "__main__":
    easyTkinter = EasyTkinter(size=(192 * 5, 108 * 5))
    easyTkinter.BuildController("testLabel", Controllers.LABEL)

    easyTkinter.SetControllerGrid("testLabel",
                                  Controllers.LABEL,
                                  row=1,
                                  column=1
                                  )
    easyTkinter.configController("testLabel", Controllers.LABEL, image=easyTkinter.toImage(
        r"E:\Python\PersonalLibrary\PersonalLibrary\EasyTkinter\resource\assets\img\test.jpg", size=(192 * 2, 108 * 2)))

    easyTkinter.start()
