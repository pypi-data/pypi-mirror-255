from PersonalLibrary.LibraryException.LibraryException import LibraryException


class NoneFileContextException(LibraryException):
    def __init__(self, errorMessage: str = None):
        if errorMessage is None:
            errorMessage = "文件内容为空，请检查 | The file content is empty, please check"
        super().__init__(errorMessage)
        self.error_code = self.error_code()
        self.errorMessage = errorMessage
