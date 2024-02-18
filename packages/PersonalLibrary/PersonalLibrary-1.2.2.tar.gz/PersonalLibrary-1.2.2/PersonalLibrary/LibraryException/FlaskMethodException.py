from PersonalLibrary.LibraryException.LibraryException import LibraryException
from PersonalLibrary.Text.Text import Text


class FlaskMethodException(LibraryException):
    def __init__(self, errorMessage: str = None):
        if errorMessage is None:
            errorMessage = Text().translate("error.flask.route_method")
        super().__init__(errorMessage)
        self.error_code = self.error_code()
        self.errorMessage = errorMessage
