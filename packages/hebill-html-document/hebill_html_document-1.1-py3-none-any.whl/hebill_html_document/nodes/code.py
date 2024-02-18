from .node import node


class code(node):
    def __init__(self, senior, text: str = None):
        super().__init__(senior)
        self.text: str = "" if text is None else text

    def output(self):
        self.document.output_next_breakable = False
        return f"{self.text}"
