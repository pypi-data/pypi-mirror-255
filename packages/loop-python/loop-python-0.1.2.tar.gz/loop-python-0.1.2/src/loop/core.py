from typing import Iterable, Iterator, TypeVar, Protocol


T = TypeVar('T')
A = TypeVar('A')
K = TypeVar('K')
R = TypeVar('R')


class Function(Protocol):
    def __call__(self, *args: A, **kwargs: K) -> R:
        ...


class Mapper:
    __slots__ = ('_args', '_kwargs', '_function')

    def __init__(self, function: Function, *args: A, **kwargs: K):
        self._args = args
        self._kwargs = kwargs
        self._function = function

    def __call__(self, inp: T) -> R:
        return self._function(inp, *self._args, **self._kwargs)


class UnpackerMapper(Mapper):
    __slots__ = ()

    def __call__(self, inp: T) -> R:
        return self._function(*inp, *self._args, **self._kwargs)


class Loop:
    def __init__(self, iterable: Iterable[T]):
        self._iterable = iterable
        self._mappers = []

    def map(self, function: Function, *args: A, **kwargs: K) -> 'Loop':
        """
        Apply `function` to each `item` in `iterable` by calling `function(item, *args, **kwargs)`.

        Example:
            --8<-- "docs/examples/map_single.md"

        Args:
            function: Function to be applied on each item in the loop.
            args: Passed as `*args` (after the loop item) to each call to `function`.
            kwargs: Passed as `**kwargs` to each call to `function`.

        Returns:
            Returns `self` to allow for further method chaining.

        !!! note

            Applying ` map(function, *args, **kwargs)` is not the same as applying `map(functools.partial(function, *args, **kwargs))` because `functools.partial` passes `*args` BEFORE the loop item.
        """
        self._mappers.append(Mapper(function, *args, **kwargs))
        return self

    def unpack_map(self, function: Function, *args: A, **kwargs: K) -> 'Loop':
        """
        This is the same as [`map()`][loop.Loop.map] except that the `item` from `iterable` is star unpacked as it is passed to `function` i.e. `function(*item, *args, **kwargs)`.
        """
        self._mappers.append(UnpackerMapper(function, *args, **kwargs))
        return self

    def exhaust(self) -> None:
        """
        Consume the loop without returning any results.

        This maybe useful when you map functions only for their side effects.
        """
        for _ in self:
            pass

    def __iter__(self) -> Iterator[R]:
        for inp in self._iterable:
            out = inp

            for mapper in self._mappers:
                out = mapper(out)

            yield out


def loop_over(iterable: Iterable[T]) -> Loop:
    """Construct a new `Loop`.

    Customize the looping behaviour by chaining different `Loop` methods and finally use a `for` statement like you normally would.

    Example:
        --8<-- "docs/examples/minimal.md"

    Args:
        iterable: The object to be looped over.

    Returns:
        Returns a new `Loop` instance wrapping `iterable`.
    """
    return Loop(iterable)
