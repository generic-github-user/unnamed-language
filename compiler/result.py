from __future__ import annotations
from typing import TypeVar, Generic, Callable, Optional, Any
T = TypeVar('T')
V = TypeVar('V')


class Result(Generic[T]):
    def __init__(self, value: T, ok: bool):
        self.value = value
        self.ok = ok

    @staticmethod
    def Ok(v):
        return Result(v, True)

    @staticmethod
    def Err(e):
        return Result(e, False)

    # ?
    def test(self, f: Callable[[T], bool]) -> Result[T]:
        if self.ok:
            if f(self.unwrap()):
                return self
            return Result.Err(f'{f} returned `False` on the wrapped value')
        return self

    def then(self, f: Callable[[T], V]) -> Result[V]:
        if not self.ok:
            return Result.Err(self.value)
        return Result.Ok(f(self.unwrap()))

    def else_(self: Result[T], f: Callable[..., T], *args) -> Result[T]:
        if self.ok:
            return self
        return Result.Ok(f(*args))

    def unwrap(self) -> T:
        if self.ok:
            return self.value
        else:
            breakpoint()
            raise ResultError(self.value)


class ResultError(Exception):
    pass
