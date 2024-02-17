import json
import os

from PersonalLibrary.Config.Config import Config
try:
    from PersonalLibrary.Text.Colors import Colors
except ModuleNotFoundError:
    from Colors import Colors


class Text:
    def __init__(self, Language: str = None, path=None):
        self.context = "None"
        self.language = Language == "" or Config().getConfigOptions('language')
        self.language = self.language.lower()
        self.path = path or os.path.abspath(__file__).split('Text.py')[0] + 'assets\\lang\\'
        ...

    def __str__(self) -> str:
        return self.context

    def of(self, context: str):
        self.context = context
        return self.context

    def translate(self, key):
        """
        接受json类型的翻译文件
        :param key: 键值
        :return: 翻译后内容
        """
        with open(self.path + self.language + '.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not data:
                self.context = "None"
                raise "文件内容为空，请检查 | The file content is empty, please check"
            else:
                self.context = data[key].replace("\n", " ").replace("\r", " ")
            return self

    def formatted(self, *args):
        return self.context.format(*args)

    def style(self, color: Colors):
        return color + self.context
