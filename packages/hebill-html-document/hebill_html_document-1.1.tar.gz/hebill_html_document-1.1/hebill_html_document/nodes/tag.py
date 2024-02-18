from .group import group


class tag(group):
    def __init__(self, senior, name: str = None):
        super().__init__(senior)
        if name is not None:
            self.name = name
        else:
            n = self.__class__.__name__
            if n[-1] == "_":
                n = n[:-1]
            n.replace("_", "_")
            self.name = n
        self.attributes: dict = {}
        self.output_breakable = True

    def output(self):
        s = ""
        if self.document.output_break:
            if self.output_breakable and self.document.output_next_breakable:
                if self.node_level > 0:
                    s += "\n"
            s += self.document.output_retraction * self.node_level
        s += "<" + self.name
        # s += self.Attributes().output()
        if len(self.attributes) > 0:
            for n, v in self.attributes.items():
                s += f" {n}=\"{v}\""
        s += ">"
        self.document.output_next_breakable = True
        si = super().output()
        s += si
        if self.document.output_break:
            if si != "" and self.document.output_next_breakable:
                s += "\n" + "	" * self.node_level
        s += "</" + self.name + ">"
        self.document.output_next_breakable = True
        return s
