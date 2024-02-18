from PersonalLibrary.LibraryException import getErrorCode


class LibraryException(Exception):
    def __init__(self, errorMessage: str):
        Exception.__init__(self)
        self.error_code = getErrorCode
        self.error_message = errorMessage

    def __str__(self):
        return f"[ERROR {self.error_code}]: {self.error_message}"
