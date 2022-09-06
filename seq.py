from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic
from option import Option, Some
from nat import Nat


@dataclass
class Nil:
    def __repr__(self) -> str:
        return '[]'


T = TypeVar('T')


@dataclass(frozen=True)
class Cons(Generic[T]):
    head: T
    tail: Seq[T]

    @staticmethod
    def __repr_tail(tail: Seq[T]) -> str:
        match tail:
            case Nil():
                return ']'

            case Cons(x, xs):
                return f', {x}{Cons.__repr_tail(xs)}'

    def __repr__(self) -> str:
        return f'[{self.head}{self.__repr_tail(self.tail)}'


Seq = Nil | Cons[T]


def lookup(index: Nat, seq: Seq[T]) -> Option[T]:
    match seq:
        case Nil():
            return None

        case Cons(x, xs):
            if index == Nat(0):
                return Some(x)
            else:
                return lookup(Nat(int(index) - 1), xs)


def from_list(list: list[T]) -> Seq[T]:
    match list:
        case [x, *xs]:
            return Cons(x, from_list(xs))

        case _:
            return Nil()


def reverse(seq: Seq[T]) -> Seq[T]:
    return __reverse(seq, Nil())


def __reverse(seq: Seq[T], reversed: Seq[T]) -> Seq[T]:
    match seq:
        case Nil():
            return reversed

        case Cons(x, xs):
            return __reverse(xs, Cons(x, reversed))
