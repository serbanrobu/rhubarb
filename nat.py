from __future__ import annotations
from dataclasses import dataclass


@dataclass(order=True)
class Nat:
    __val: int

    def __init__(self, val: int) -> None:
        self.__val = 0 if val < 0 else val

    def __int__(self) -> int:
        return self.__val

    def __repr__(self) -> str:
        return f'{self.__val}'

    def __add__(self, other: Nat) -> Nat:
        return Nat(self.__val + other.__val)
