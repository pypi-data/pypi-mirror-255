from ..nodes import tag


class div(tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, None)
        self.output_break_inner = False
        if text is not None:
            self.create().node().content(text)
