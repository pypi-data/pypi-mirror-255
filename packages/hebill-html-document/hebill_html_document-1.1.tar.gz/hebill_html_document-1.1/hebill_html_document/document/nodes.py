class nodes:
    def __init__(self, senior):
        self.senior = senior

    def code(self, text: str = None):
        from ..nodes.code import code
        return code(self.senior, text)

    def content(self, text: str = None):
        from ..nodes.content import content
        return content(self.senior, text)

    def comment(self, text: str = None):
        from ..nodes.comment import comment
        return comment(self.senior, text)

    def group(self):
        from ..nodes.group import group
        return group(self.senior)

    def tag(self, name: str):
        from ..nodes.tag import tag
        return tag(self.senior, name)
