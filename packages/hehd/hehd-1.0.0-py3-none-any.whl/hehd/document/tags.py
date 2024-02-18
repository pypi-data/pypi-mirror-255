class tags:
    def __init__(self, senior):
        self.senior = senior

    def a(self, title: str = None, url: str = None):
        from ..tags.a import a
        return a(self.senior, title, url)

    def body(self):
        from ..tags.body import body
        return body(self.senior)

    def div(self, text: str = None):
        from ..tags.div import div
        return div(self.senior, text)

    def head(self):
        from ..tags.head import head
        return head(self.senior)

    def html(self, lang: str = None):
        from ..tags.html import html
        return html(self.senior, lang)

    def input_text(self, name: str = None, value: str | int | float = None, placeholder: str = None):
        from ..tags.input_text import input_text
        return input_text(self.senior, name, value, placeholder)

    def link(self, url: str = None):
        from ..tags.link import link
        return link(self.senior, url)

    def span(self, text: str = None):
        from ..tags.span import span
        return span(self.senior, text)

    def title(self, text: str = None):
        from ..tags.title import title
        return title(self.senior, text)
