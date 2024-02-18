from __future__ import annotations


class node:
    def __init__(self, senior):
        self._node_id = id(self)
        from hebill_html_document.main import document
        from ..nodes.group import group
        self.node_document: document
        self.node_senior: group | None = None
        if isinstance(senior, document):
            self.document = senior
        elif isinstance(senior, group):
            self.node_senior = senior
            self.document = senior.document
            self.node_senior.juniors[self.node_id] = self
        self.document.elements[self.node_id] = self
        self.node_output_breakable = False

    @property
    def node_id(self) -> int:
        return self._node_id

    @property
    def node_level(self) -> int:
        if self.node_senior is None:
            return 0
        from ..nodes.tag import tag
        from ..nodes.group import group
        if isinstance(self, group) and not isinstance(self, tag):
            return self.node_senior.node_level
        return self.node_senior.node_level + 1

    def output(self) -> str:
        pass
