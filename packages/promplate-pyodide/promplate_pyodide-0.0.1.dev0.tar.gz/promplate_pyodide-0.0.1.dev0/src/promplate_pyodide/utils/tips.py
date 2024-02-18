class Tips:
    def __init__(self, text: str):
        self.text = text

    def __await__(self):
        yield None
        return self

    def __repr__(self) -> str:
        return f"<{self.text}>"
