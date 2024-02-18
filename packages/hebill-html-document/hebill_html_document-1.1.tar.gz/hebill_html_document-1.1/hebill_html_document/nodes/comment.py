from .node import node


class comment(node):
    def __init__(self, senior, text: str = None):
        super().__init__(senior)
        self.text: str = "" if text is None else text

    def output(self):
        import html
        s = ""
        if self.document.output_break:
            s += "\n" + self.document.output_retraction * self.node_level
        s += f"<!--[{html.escape(self.text)}]-->"
        self.document.output_next_breakable = True
        return s
