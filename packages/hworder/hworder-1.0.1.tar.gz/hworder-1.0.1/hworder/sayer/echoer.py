__all__ = ["Echoer"]


class Echoer:
    def __init__(self):
        pass

    def __call__(self, value: str):
        return f"{value}, {value}"
