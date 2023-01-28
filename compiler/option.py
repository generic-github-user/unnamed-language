from __future__ import annotations
from typing import TypeVar, Generic, Optional, Callable, Any
T = TypeVar('T')
V = TypeVar('V')


class Option(Generic[T]):
    """A monadic type representing a value that may or may not be present;
    useful for (e.g.) representing the result of a search operation for a value
    which is not guaranteed to exist. Is generic in `T`. Contains various
    convenience methods to support functional programming approaches to error
    handling (is very much a WIP). Loosely modelled after Rust's `Option` type
    and Haskell's `Maybe` type. See https://en.wikipedia.org/wiki/Option_type
    for more information."""

    def __init__(self, value: Optional[T], some: bool):
        self.value = value
        self.is_some = some

    @staticmethod
    def some(v: T) -> Option[T]:
        """Returns an `Option` variant containing a value."""
        return Option(v, True)

    @staticmethod
    def none(v=None) -> Option[T]:
        """Returns an `Option` variant with no inner value."""
        return Option(v, False)

    def then(self, f: Callable[[T], V]) -> Option[V]:
        """If `self` is a none-Option, returns the equivalent in `V`; if `self`
        has a value, calls `f` using the value and wraps the result in another
        `Option`."""

        if not self.is_some:
            return Option.none(self.value)
        assert self.value is not None
        return Option.some(f(self.unwrap()))

    def else_(self, f: Callable[..., T], *args) -> Option[T]:
        """Returns `self` if it is a some-Option; otherwise, returns the result
        of `f` on `args`, wrapped in an `Option` type."""

        if self.is_some:
            return self
        return Option.some(f(*args))

    def unwrap(self, message: str = '') -> T:
        """Returns `self`'s wrapped value if it has one; raises an exception
        otherwise."""

        if self.is_some:
            assert self.value is not None
            return self.value
        else:
            raise OptionError(self.value)

    def __eq__(self: Option[T], other: Option[T]) -> bool:
        return (self.is_some == other.is_some) and (self.value == other.value)

    def __hash__(self: Option[T]) -> int:
        return hash(self.value)


class OptionError(Exception):
    pass
