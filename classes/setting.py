from typing import Any

class Setting:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Setting(name={self.name}, value={self.value})"