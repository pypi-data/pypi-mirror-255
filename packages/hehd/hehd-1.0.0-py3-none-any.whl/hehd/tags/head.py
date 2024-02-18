from ..nodes import tag


class head(tag):
    def __init__(self, senior):
        super().__init__(senior)
        self._metas = self.create().node().group()
        self._libraries = self.create().node().group()
        self._title = self.create().tag().title()

    @property
    def metas(self):
        return self._metas.create().tag().title()

    @property
    def libraries(self):
        return self._libraries

    @property
    def title(self):
        return self._title
