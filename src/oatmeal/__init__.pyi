from typing import Any

class Point:
    x: int
    y: int

    def clone(self) -> Point: ...
    def __init__(self, x: int, y: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> int: ...
    def __setitem__(self, index: int, value: int) -> int: ...
    def __add__(self, other: Point) -> Point: ...
    def __sub__(self, other: Point) -> Point: ...
    def __mul__(self, other: int) -> Point: ...
    def __truediv__(self, other: int) -> Point: ...
    def __floordiv__(self, other: int) -> Point: ...
    def __mod__(self, other: int) -> Point: ...
    def __neg__(self) -> Point: ...
    def __abs__(self) -> Point: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def __hash__(self) -> int: ...