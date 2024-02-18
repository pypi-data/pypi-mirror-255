import os
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PersonalLibrary.LibraryException.ConfigOptionException import ConfigOptionException


class Config:
    def __init__(self, configPath: str = None) -> None:
        self.configPath: str = configPath
        self._configOptions: list[str] = ['language']

    # def _setPath(self):
    #     path: str = os.path.abspath(os.path.dirname(__file__)).split("Config.json")[0]
    #     self.configPath = path + self.configPath
    #     return self.configPath.replace('\\', '/')

    def getConfig(self):
        with open(self.configPath, "r", encoding="utf-8") as file:
            return json.load(file)

    def setConfig(self, **options):
        with open(self.configPath, "w", encoding="utf-8") as file:
            configDict = json.load(file)
            file.close()
        for key in options.keys():
            if key in self._configOptions:
                configDict[key] = options[key]
            else:
                raise ConfigOptionException(key)

    def get(self):
        return "Config(\n" + ",\n".join(self._configOptions) + "\n)"

    def getConfigOptions(self, options: str) -> str:
        if options in self._configOptions:
            return self.getConfig()[options]
        else:
            raise ConfigOptionException(options)

    def generateConfig(self, configPath: str = None) -> None:
        if configPath is None:
            configPath = self.configPath
        with open(configPath, "w", encoding="utf-8") as file:
            json.dump({k: "" for k in self._configOptions}, file)
            return None

    def getLanguage(self) -> str:
        if self.configPath is None:
            return 'zh_cn'
        else:
            return self.getConfigOptions('language')


if __name__ == "__main__":
    config = Config()
