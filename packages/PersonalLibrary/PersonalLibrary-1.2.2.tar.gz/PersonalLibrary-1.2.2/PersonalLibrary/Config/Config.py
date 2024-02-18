import os
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PersonalLibrary.LibraryException.ConfigOptionException import ConfigOptionException


class Config:
    configPath: str = r"/assets/config.json"
    configOptions: list = ['language']

    def _setPath(self):
        path: str = os.path.abspath(os.path.dirname(__file__)).split("Config.json")[0]
        self.configPath = path + self.configPath
        return self.configPath.replace('\\', '/')

    def getConfig(self):
        with open(self._setPath(), "r", encoding="utf-8") as file:
            return json.load(file)

    def setConfig(self, **options):
        with open(self.configPath, "w", encoding="utf-8") as file:
            configDict = json.load(file)
            file.close()
        for key in options.keys():
            if key in self.configOptions:
                configDict[key] = options[key]
            else:
                raise ConfigOptionException(key)

    def get(self):
        return "Config(\n" + ",\n".join(self.configOptions) + "\n)"

    def getConfigOptions(self, options: str) -> str:
        if options in self.configOptions:
            return self.getConfig()[options]
        else:
            raise ConfigOptionException(options)


if __name__ == "__main__":
    config = Config()
