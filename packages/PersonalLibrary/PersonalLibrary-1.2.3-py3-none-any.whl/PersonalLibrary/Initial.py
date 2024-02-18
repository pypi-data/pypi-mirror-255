import importlib

from PersonalLibrary.LibraryLogger.LibraryLogger import LibraryLogger
from PersonalLibrary.Text.Text import Text

SupportModule: list = ['numpy', 'pandas', 'matplotlib', 'math', 'scipy', 'requests', 'beautifulsoup4', 'flask']

Logger: LibraryLogger = LibraryLogger()


@Logger.ShowLog
def importModule(*moduleName: str):
    for module in moduleName:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            Logger.error(Text().translate('error.import.not_exist').formatted(module))
            return False
    return True
