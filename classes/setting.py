from typing import Any

class Setting:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def format_value(self) -> str:
        try:
            if not (self.value_is_primitive(self.value)):
                raise ValueError(f"Value for {self.name} is not a primitive type. Must be str, int, float, bool, or None.")

            return str(self.value).lower() if isinstance(self.value, bool) else str(self.value)
        except ValueError as e:
            print(f"Error formatting value for {self.name}: {e}")
            return str(self.value)

    def __repr__(self):
        return f"{self.name} = {self.format_value()}\n"
    
    def value_is_primitive(self, value: Any) -> bool:
        return isinstance(value, (str, int, float, bool, type(None)))