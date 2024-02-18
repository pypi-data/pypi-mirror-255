from .nodes import nodes
from .tags import tags


class create:
    def __init__(self, senior):
        self.senior = senior
        self._nodes = nodes(self.senior)
        self._tags = tags(self.senior)

    def node(self):
        return self._nodes

    def tag(self):
        return self._tags
