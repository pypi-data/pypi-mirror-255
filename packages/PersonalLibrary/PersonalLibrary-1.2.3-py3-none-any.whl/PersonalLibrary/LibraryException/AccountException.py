from PersonalLibrary.LibraryException.LibraryException import LibraryException
from PersonalLibrary.Text.Text import Text


class AccountException(LibraryException):
    def __init__(self, errorMessage: str = None):
        if errorMessage is None:
            errorMessage = Text().translate("error.easy_sql.connection_error.account_error")
        super().__init__(errorMessage)
        self.error_code = self.error_code()
        self.errorMessage = errorMessage
