from typing import Any

from PersonalLibrary.LibraryException.LibraryException import LibraryException
from PersonalLibrary.Text.Text import Text


class ConfigOptionException(LibraryException):
    def __init__(self, errorMessage: str = None, *args: Any):
        if errorMessage is None:
            errorMessage = Text().translate("error.config_option_exception").formatted(", ".join([i for i in args]))
        super().__init__(errorMessage)
        self.error_code = self.error_code()
        self.errorMessage = errorMessage
