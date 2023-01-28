from __future__ import annotations
import itertools
from .result import Result
from .option import Option

from typing import TypeVar, Generic, Iterable, Optional, Callable, Any
T = TypeVar('T')
V = TypeVar('V')


class List(Generic[T]):
    """A simple wrapper class for several built-in Python sequence types
    designed to facilitate method chaining and functional programming patterns.
    In many cases, this class' methods simply pass calls to standard global
    functions on iterators included in Python (e.g., `map` and `filter`). There
    are currently some efficiency concerns, namely in cases where I have
    temporarily avoided headaches by converting iterators directly to lists; I
    plan to refactor these later to improve style and efficiency at the
    potential cost of a slightly more complicated interface (and more involved
    internals)."""

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        """Creates a new list containing the elements from the Python list
        `items` (i.e., wrapping it)"""

        if items is None:
            items = []
        self.items: list[T] = list(items)

    @staticmethod
    def concat(lists: List[List[T]]) -> List[T]:
        return List(list(itertools.chain.from_iterable(lists)))

    def for_each(self, f: Callable[[T], Any]) -> None:
        for x in self:
            f(x)

    def find_if(self, f: Callable[[T], bool], message=None) -> Option[T]:
        matches = self.filter(f)
        if matches.length() == 0:
            return Option.none(message or f'List `{self.to_string()}` does not contain element matching predicate `{f}`')
        else:
            return Option.some(matches[0])

    def map(self, f: Callable[[T], V]) -> List[V]:
        """Applies `f` to each element in this list, returning a new list"""

        return List(list(map(f, self.items)))

    def filter(self, p: Callable[[T], bool]) -> List[T]:
        """Returns a new list containing only the elements in this list for
        which the predicate `p` is true"""
        return List(list(filter(p, self.items)))

    def filter_by(self, attr: str, value: Any) -> List[T]:
        """Returns a new list containing elements for which the attribute
        `attr` is equal to `value`"""

        return self.filter(lambda x: getattr(x, attr) == value)

    def remove(self, *args) -> List[T]:
        """Removes items equal to any of the arguments, returning a new list"""

        return self.filter(lambda x: x not in args)

    def get(self, attr: str) -> List[Any]:
        """Returns a new list constructed by accessing the `attr` attribute of
        each item in this list"""

        return self.map(lambda x: getattr(x, attr))

    def set(self, attr: str, value: Any) -> List[T]:
        for x in self.items:
            setattr(x, attr, value)
        return self

    def sorted(self, f) -> List[T]:
        """Returns a new list sorted using the comparison function `f`, which
        should take as input two elements of the input list"""

        return List(list(sorted(self.items, key=f)))

    def all(self, p: Optional[Callable[[T], bool]] = None) -> bool:
        """Returns true if and only if the predicate `p` is true for every
        element in the list"""

        if p is None:
            return all(self.items)
        else:
            return all(p(i) for i in self.items)

    def any(self, p: Optional[Callable[[T], bool]] = None) -> bool:
        """Returns true if and only if the predicate `p` is true for at least
        one element in the list"""

        if p is None:
            return any(self.items)
        else:
            return any(p(i) for i in self.items)

    def none(self, p: Optional[Callable[[T], bool]] = None) -> bool:
        """Returns true if and only if the predicate `p` is false for every
        element in the list, or (equivalently) true for no elements"""

        return not self.any(p)

    def len(self) -> int:
        """Returns an integer representing the length of this list"""

        return len(self.items)

    def append(self, x: T) -> None:
        """Adds a new element to this list (modifying it in place)"""

        return self.items.append(x)

    def extend(self, x: Iterable[T]) -> List[T]:
        self.items.extend(x)
        return self

    def join(self, s: str) -> str:
        """Combine the elements of the list in order, returning a string; if
        the given delimiter has length m and this list has length n, the
        resulting string will be m*(n-1) characters longer than the
        concatenation of the string representations of all the elements in the
        list"""

        return s.join(self.map(str).items)

    def partition(self, attr: str) -> dict:
        return {value: self.filter(lambda x: getattr(x, attr) == value) for
                value in set(getattr(y, attr) for y in self.items)}

    def length(self):
        return len(self)

    def to_string(self, **kwargs) -> str:
        return self.map(lambda x: x.to_string(**kwargs)).join(', ')

    def index(self, x: T) -> Result[int]:
        return Result.Ok(self.items.index(x))

    def contains(self, x: T) -> bool:
        return x in self.items

    def __hash__(self) -> int:
        return hash(x for x in self.items) # ?

    def __bool__(self) -> bool:
        return self.length() != 0

    def __add__(self, other: List[T] | list[T]) -> List[T]:
        if isinstance(other, List):
            other = other.items
        return List(self.items + other)

    def __iter__(self):
        return self.items.__iter__()

    def __len__(self):
        return self.len()

    def __getitem__(self, i):
        return self.items[i]

    def __eq__(self, other):
        return self.items == other.items

    def __repr__(self):
        return repr(self.items)
