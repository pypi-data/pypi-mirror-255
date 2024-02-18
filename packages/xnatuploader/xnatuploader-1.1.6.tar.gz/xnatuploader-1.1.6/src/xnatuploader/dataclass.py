
from dataclasses import dataclass

@dataclass
class Foo:
    """A sample dataclass"""
    a: str
    b: int
    c: float

    def __post_init__(self):
        self.d = "fnar"

    def say(self):
        print(self.a)
        print(self.b)
        print(self.c)
        print(self.d)