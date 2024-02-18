from ..nodes import tag


class link(tag):
    def __init__(self, senior, url: str = None):
        super().__init__(senior)
        if url is not None:
            self.attributes["href"] = url
