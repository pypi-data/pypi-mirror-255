from bs4 import BeautifulSoup

from PersonalLibrary.EasyRequest.EasyRequest import EasyRequest
from PersonalLibrary.Initial import Logger, importModule
from PersonalLibrary.EasyHtmlProgress.Tags import Tags
from PersonalLibrary.Text.Text import Text

if importModule("bs4"):
    from bs4 import BeautifulSoup

    Logger.hide_log()


class EasyHtmlProgress:

    def __init__(self, html: str, encoding: str = 'utf-8', **kwargs) -> None:
        Logger.getLogger(self.__class__.__name__)
        self.parsers: list = ['html.parser', 'lxml', 'xml', 'html5lib']
        self.parser = self.parsers[0]
        self.html: str = html
        self.encoding: str = encoding
        try:
            self.soup = BeautifulSoup(self.html, features=self.parser, **kwargs)
        except AttributeError:
            Logger.error(Text().translate("error.progress.html_is_none"))
            self.soup = BeautifulSoup("", features=self.parser, **kwargs)

    def getSoup(self) -> BeautifulSoup:
        return self.soup

    def getHrefs(self, tag: Tags, conditions=None) -> list:
        """
        返回某个标签下的所有超链接
        <a href>
        <others src>
        :param conditions接受来自筛选的条件，如 class=... id=... name=...，以字典的形式传入
        :param tag: Html标签
        :return: 超链接的列表
        """
        if conditions is None:
            conditions = dict()

        tag = str(tag)
        tags = self.soup.find_all(tag, **conditions)
        if tag == Tags.A:
            return [element.get('href') for element in tags]
        else:
            return [element.get('src') for element in tags]

    @staticmethod
    def _clearChars(elements: list[str], clearChars: list) -> list:
        if clearChars is not None:
            return [element.replace(clearChar, '') for clearChar in clearChars for element in elements]
        else:
            return elements

    @staticmethod
    def _deleteNullValues(elements: list[str]) -> list:
        return [element for element in elements if element != '']

    def getTexts(self, tag: Tags, conditions=None, clearChars: list[str] = None, ignoreNone: bool = False) -> list:
        tag = str(tag)

        if conditions is None:
            conditions = {}

        tags = self.soup.find_all(tag, **conditions)
        originList = [element.text for element in tags]
        cleanList = self._clearChars(originList, clearChars)
        if ignoreNone:
            return self._deleteNullValues(cleanList)
        else:
            return cleanList

    @staticmethod
    def DecodeText(texts: list[str], encode: str = 'latin1', decode: str = 'utf-8') -> list:
        contexts = []
        for context in texts:
            try:
                contexts.append(context.encode(encode).decode(decode))
            except UnicodeEncodeError:
                Logger.warning(Text().translate("warning.unicode_encode_error").formatted(context, encode, decode))
                contexts.append(context)
        return contexts


if __name__ == '__main__':
    easyRequest = EasyRequest()
    Logger.show_log()
    easyRequest.request('get', 'https://www.bilibili.com/')
    easyHtml = EasyHtmlProgress(easyRequest.getText())
    text = easyHtml.getTexts(Tags.A, clearChars=['\n'], ignoreNone=True)
    print(text)
