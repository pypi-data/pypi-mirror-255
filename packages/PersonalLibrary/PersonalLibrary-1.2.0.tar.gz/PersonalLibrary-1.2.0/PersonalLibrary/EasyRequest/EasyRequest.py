from typing import Self

from requests import Response, Session

from PersonalLibrary.LibraryException.ConnectionExption import ConnectionException
from PersonalLibrary.Initial import importModule, Logger
from PersonalLibrary.Text.Text import Text

if importModule("requests"):
    import requests

    Logger.hide_log()


class EasyRequest:
    def __init__(self):
        Logger.getLogger(self.__class__.__name__)
        self.POST = 'post'
        self.GET = 'get'
        self.request_code = int()
        self.session: Session = requests.Session()
        self.response: Response = Response()
        self.text = Text()
        self.agreements = ['http://', 'https://', 'ftp://', 'ftps://', 'file://']

        self.headers: dict[str, dict[str, str]] = {
            "FireFox": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"},
            "Chrome": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
        }
        self.referer: str = ""
        self.header: str = "Chrome"
        if not self._NetworkTest():
            raise ConnectionException()

    @Logger.ShowLog
    def _NetworkTest(self):
        try:
            response = requests.get("https://www.baidu.com", headers=self.headers[self.header])
            if response.status_code != 200:
                Logger.error(Text().translate("error.requests.web_connection"))
                return False
            else:
                return True
        except requests.exceptions.ConnectionError:
            Logger.error(Text().translate("error.requests.web_connection"))
            return False

    def clearReferer(self):
        self.referer = ""
        return self

    def _url(self, url: str, agreement='http://') -> str:
        if not url.startswith(tuple(self.agreements)) and agreement in self.agreements:
            return agreement + url
        return url

    def request(self, method, url, data=None, param=None, headers=None, cookies=None, timeout: int = 120,
                **kwargs) -> Self:

        if headers is None:
            headers = self.headers[self.header.title()]

        if self.referer != "":
            headers["Referer"] = self.referer

        try:
            url = self._url(url)
            if method == self.POST:
                self.response = requests.post(url, data=data, params=param, headers=headers, cookies=cookies,
                                              timeout=timeout, **kwargs)
                self.request_code = self.response.status_code
                Logger.info(self.text.translate('info.requests.response.status_code').formatted(self.request_code))
                return self
            elif method == self.GET:
                self.response = requests.get(url, data=data, params=param, headers=headers, cookies=cookies,
                                             timeout=timeout, **kwargs)
                self.request_code = self.response.status_code
                Logger.info(self.text.translate('info.requests.response.status_code').formatted(self.request_code))
                return self
            else:
                Logger.error(self.text.translate('error.requests.method'))
        except requests.exceptions.ConnectTimeout:
            Logger.error(self.text.translate('error.requests.connect_timeout').formatted(url, timeout))

    def session(self, method, url, data=None, param=None, headers=None, cookies=None, timeout: int = 120,
                **kwargs) -> requests.Response:

        if headers is None:
            self.session.headers = self.headers[self.header.title()]

        if self.referer != "":
            self.session.headers["Referer"] = self.referer

        try:
            url = self._url(url)
            if method == self.POST:
                self.response = self.session.post(url, data=data, params=param, headers=headers, cookies=cookies,
                                                  timeout=timeout, **kwargs)
                self.request_code = self.response.status_code
                Logger.info(self.text.translate('info.requests.response.status_code').formatted(self.request_code))
                return self.response
            elif method == self.GET:
                self.response = self.session.get(url, data=data, params=param, headers=headers, cookies=cookies,
                                                 timeout=timeout, **kwargs)
                self.request_code = self.response.status_code
                Logger.info(self.text.translate('info.requests.response.status_code').formatted(self.request_code))
                return self.response
            else:
                Logger.error(self.text.translate('error.requests.method'))
        except requests.exceptions.ConnectTimeout:
            Logger.error(self.text.translate('error.requests.connect_timeout').formatted(url, timeout))

    def RJson(self, response: Response = None) -> dict:
        try:
            if response is None and self.response is None:
                Logger.error(self.text.translate('error.requests.not_exist'))
            elif response is None and self.response is not None:
                response = self.response
                if response.json():
                    return response.json()
                else:
                    Logger.warning(self.text.translate('error.requests.response_json_not_exist'))
                    return dict()
            else:
                if response.json():
                    return response.json()
                else:
                    Logger.warning(self.text.translate('error.requests.response_json_not_exist'))
                    return dict()
        except requests.exceptions.JSONDecodeError:
            Logger.error(self.text.translate('error.requests.response_json_not_exist'))
            return dict()

    @Logger.ToFile(r"E:\Python\PersonalLibrary\static\log")
    def getText(self) -> str:
        Logger.info(self.text.translate('info.requests.response.text'))
        return self.response.text
