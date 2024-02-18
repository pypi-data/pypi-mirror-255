import json
import os
from typing import Any

from PersonalLibrary.Config.Config import Config
from PersonalLibrary.LibraryException.NoneFileContextException import NoneFileContextException

try:
    from PersonalLibrary.Text.Colors import Colors
except ModuleNotFoundError:
    from Colors import Colors


class Text:
    def __init__(self, Language: str = None, path=None):
        self.context = "None"
        self.language = Language == "" or Config().getLanguage()
        self.language = self.language.lower()
        self.path = path or os.path.abspath(__file__).split('Text.py')[0] + 'assets\\lang\\'
        ...

    def __str__(self) -> str:
        return self.context

    def of(self, context: Any):
        self.context = str(context)
        return self.context

    def translate(self, key):
        """
        接受json类型的翻译文件
        :param key: 键值
        :return: 翻译后内容
        """
        try:
            with open(self.path + self.language + '.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not data:
                    self.context = "None"
                    raise NoneFileContextException()
                else:
                    self.context = data[key].replace("\n", " ").replace("\r", " ")
                return self
        except FileNotFoundError:
            raise FileNotFoundError(
                f"未在{self.path + self.language + '.json'}下找到翻译文件，请检查！| Translation file not found under {self.path + self.language + '.json'}, please check!")

    def formatted(self, *args):
        return self.context.format(*args)

    def style(self, color: Colors):
        return color + self.context
