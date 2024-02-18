from ..nodes import tag


class html(tag):
    def __init__(self, senior, lang: str = None):
        super().__init__(senior)
        if lang is not None:
            self.attributes["lang"] = lang
        self.__head = self.create().tag().head()
        self.__body = self.create().tag().body()

    @property
    def head(self):
        return self.__head

    @property
    def body(self):
        return self.__body
