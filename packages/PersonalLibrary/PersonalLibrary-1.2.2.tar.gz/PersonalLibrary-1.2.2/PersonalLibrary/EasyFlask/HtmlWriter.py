from PersonalLibrary.EasyHtmlProgress.Tags import Tags
from PersonalLibrary.Initial import Logger
from PersonalLibrary.Text.Text import Text


class HtmlWriter:
    def __init__(self, writer: str):
        self.writer = writer
        self.Logger = Logger
        self.Logger.getLogger(self.__class__.__name__ + f": {writer}")

    @staticmethod
    def writeALine(tags: Tags, content: str | Text, hasLinebreaks: bool = False, **options):
        firstTags: str = f"<{tags} "
        tailTags: str = f" </{tags}>"
        for option, values in options.items():
            firstTags += f'{option}="{values}" '
        tempValues = list(firstTags)
        tempValues[-1] = "> "
        firstTags = "".join(tempValues)
        if hasLinebreaks:
            return firstTags + content + tailTags + '\n' + "</br>"
        else:
            firstTags + content + tailTags + '\n'


if __name__ == "__main__":
    htmlWriter = HtmlWriter("self")
    htmlWriter.writeALine(Tags.DIV, "content", True, text="Hello World", style="className")
