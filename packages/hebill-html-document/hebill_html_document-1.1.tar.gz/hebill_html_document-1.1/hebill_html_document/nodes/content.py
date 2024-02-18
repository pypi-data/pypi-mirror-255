from .node import node


class content(node):
    def __init__(self, senior, text: str = None):
        super().__init__(senior)
        self.text: str = "" if text is None else text

    def output(self):
        import html
        s = html.escape(self.text)
        self.document.output_next_breakable = False
        return s
