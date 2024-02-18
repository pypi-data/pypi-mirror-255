from ..nodes import tag


class input_text(tag):
    def __init__(self, senior, name: str = None, value: str | int | float = None, placeholder: str = None):
        super().__init__(senior, "input")
        self.output_break_inner = False
        self.value: str | int | float = "" if value is None else value
        if name is not None:
            self.attributes["name"] = name
        if placeholder is not None:
            self.attributes["placeholder"] = placeholder
