from .node import node


class group(node):
    def __init__(self, senior):
        super().__init__(senior)
        self.juniors: dict = {}
        from ..document.create import create
        self._create = create(self)

    def create(self):
        return self._create

    def output(self):
        s = ""
        if len(self.juniors) > 0:
            for key, value in self.juniors.items():
                if isinstance(value, node):
                    s += value.output()
        return s
