from ..nodes import tag


class a(tag):
    output_break_inner = False

    def __init__(self, senior, text: str = None, url: str = None):
        super().__init__(senior)
        if text is not None:
            self.create().node().content(text)
        self.attributes["href"] = ""
        if url is not None:
            self.attributes["href"] = url
