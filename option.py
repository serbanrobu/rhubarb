from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar('T')


@dataclass(frozen=True)
class Some(Generic[T]):
    value: T


Option = None | Some[T]
