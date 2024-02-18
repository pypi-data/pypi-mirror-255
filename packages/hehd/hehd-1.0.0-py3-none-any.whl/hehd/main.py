from __future__ import annotations


class document:
    def __init__(self):
        self.elements: dict = {}
        self.titles: list = []
        self.title_delimiter: str = " > "
        self.output_break: bool = True
        self.output_retraction: str = "	"
        self.output_next_breakable: bool = True
        from .tags import html
        self.html: html = html(self)
        from .document.create import create
        self._create = create(self)

    def create(self):
        return self._create

    def output(self) -> str:
        if len(self.titles) > 0:
            self.html.head.title.content.text = self.title_delimiter.join(self.titles)
        s = "<!DOCTYPE html>"
        if self.output_break:
            s += "\n"
        s += self.html.output()
        return s
