import datetime
import os
import traceback
from typing import Final, Literal, Any, Union

from PersonalLibrary.Text.Colors import Colors
from PersonalLibrary.Text.Text import Text


class LibraryLogger:
    def __init__(self):
        self.logger = self.__class__.__name__
        self.logMessage: str | Text = ""
        self.logLevels: Final[tuple] = ("DEBUG", "INFO", "WARNING", "ERROR")
        self.logLevel: str = self.logLevels[1]
        self.logTime = lambda: datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.showLog = False
        self.logPath: str = os.path.abspath(os.path.dirname(__file__))
        self.cacheLog: dict[str, list] = dict[str, list]()

    def __repr__(self):
        return "Class: LibraryLogger\nFunction:" + "; ".join([i for i in self.__dict__]) + "\n"

    def setMessage(self):
        print(Colors.RESET, end='\r')
        logMessage: str = "[%s %s] (%s) %s" % (self.logTime(), self.logLevel, self.logger, self.logMessage)
        if self.cacheLog.get(self.logTime().replace('/', '-').split(" ")[0]) is None:
            self.cacheLog[self.logTime().replace('/', '-').split(" ")[0]] = [logMessage]
        else:
            self.cacheLog[self.logTime().replace('/', '-').split(" ")[0]].append(logMessage)
        return logMessage

    def __str__(self):
        print(Colors.RESET, end='\r')
        self.logMessage: str = str(self.logMessage)
        # 格式：[time](logger) message
        if self.logLevel == "WARNING":
            self.logLevel = Colors.YELLOW + self.logLevel
            self.logMessage = Colors.YELLOW + self.logMessage
        elif self.logLevel == "ERROR":
            self.logLevel = Colors.RED + self.logLevel
            self.logMessage = Colors.RED + self.logMessage

        return f"[%s %s{Colors.RESET}] {Colors.GREEN}(%s) %s" % (
            Colors.GREEN + self.logTime(), self.logLevel, Colors.GREEN + self.logger, self.logMessage + Colors.RESET
        )

    def getLogger(self, logger: str):
        self.logger = logger
        return self

    def info(self, message: Text):
        self.logMessage = message
        self.logLevel = "INFO"
        self.setMessage()
        if self.showLog:
            print(self.__str__())
        else:
            return self.__str__()

    def debug(self, message: Text):
        self.logMessage = message
        self.logLevel = "DEBUG"
        self.setMessage()
        print(self.__str__())
        return self.__str__()

    def warning(self, message: Text):
        self.logMessage = message
        self.logLevel = "WARNING"
        self.setMessage()
        if self.showLog:
            print(self.__str__())
        else:
            return self.__str__()

    def error(self, message: Text):
        self.logMessage = message
        self.logLevel = "ERROR"
        self.setMessage()
        if self.showLog:
            print(self.__str__())
        else:
            return self.__str__()

    def ShowLog(self, func: callable):
        def function(*args, **kwargs):
            self.showLog = True
            return func(*args, **kwargs)

        return function

    def show_log(self):
        self.showLog = True
        return None

    def hide_log(self):
        self.showLog = False

    def HideLog(self):
        self.showLog = False

    def setLogPath(self, path: str):
        self.logPath = path

    def _toFile(self, file: str, mode: Literal['r', 'a', 'w'] = 'r') -> None:
        try:
            with open(file + '.log', mode, encoding='utf-8') as files:
                if mode == 'r':
                    if files.read() in ("", "\n"):
                        self._toFile(file, 'w')
                    else:
                        self._toFile(file, 'a')
                elif mode == 'a':
                    logList = self.cacheLog[self.logTime().replace('/', '-').split(" ")[0]]
                    buffer = "\n".join(logList) + "\n"
                    files.write(buffer)
                else:
                    self._toFile(file, 'a')
        except FileNotFoundError:
            self._toFile(file, 'w')

    def ToFile(self, logPath: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                self.toFile(logPath)
                return result

            return wrapper

        return decorator

    def tempShow(self, context: Union[str, callable]):
        self.showLog = True
        if isinstance(context, str):
            print(context)
        else:
            context()
        self.showLog = False
        return None

    def toFile(self, logPath: str) -> None:
        self._toFile(logPath + "\\" + str(self.logTime()).replace('/', '-').split(" ")[0])

    def ShowLogClass(self, cls: Any):
        self.showLog = True
        return cls
