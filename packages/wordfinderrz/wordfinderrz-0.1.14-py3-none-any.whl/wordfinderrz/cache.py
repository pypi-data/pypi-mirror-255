from collections import UserDict
from collections.abc import Callable, Hashable, Mapping
from functools import wraps
from typing import Generic, NamedTuple, ParamSpec, TypeVar, cast, overload

P = ParamSpec("P")
T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")
_Key = tuple[Hashable, ...]


class _MaxSizedDict(UserDict[KT, VT]):
    """Dict that trims the oldest entries when a max length is reached."""

    def __init__(
        self, data: Mapping[KT, VT] | None = None, /, maxsize: int | None = None
    ) -> None:
        """Create a MaxSizedDict."""
        self.maxsize = maxsize
        super().__init__(data)

    def __setitem__(self, key: KT, item: VT) -> None:
        length = len(self)
        maxsize = self.maxsize
        if maxsize is not None and (
            length > maxsize or (length == maxsize and key not in self)
        ):
            del self.data[next(iter(self))]
        return super().__setitem__(key, item)


class CacheInfo(NamedTuple):
    """Properties of cache-decorated function."""

    hits: int
    misses: int
    maxsize: int | None
    currsize: int


class _Sentinel:
    """Arbitrary object."""


_SENTINEL = _Sentinel()


class _CacheWrapper(Generic[P, T]):
    """Wrapper object for cached functions."""

    cache_info: Callable[[], CacheInfo]
    cache: _MaxSizedDict[_Key, T]

    def __init__(self, func: Callable[P, T]) -> None:
        self.__wrapped__ = func
        wraps(func)(self)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.__wrapped__(*args, **kwargs)

    def clear_cache(self) -> None:
        self.cache.clear()


def _make_key(
    args: tuple[Hashable, ...], kwargs: dict[str, Hashable], typed: bool
) -> _Key:
    result = *args, _SENTINEL, *kwargs.items()
    if typed:
        result += (
            _SENTINEL,
            *(type(arg) for arg in args),
            _SENTINEL,
            *((k, type(v)) for k, v in kwargs.items()),
        )
    return result


@overload
def cache(
    func: None = None, *, maxsize: int | None = None, typed: bool = False
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


@overload
def cache(
    func: Callable[P, T], *, maxsize: int | None = None, typed: bool = False
) -> Callable[P, T]: ...


def cache(
    func: Callable[P, T] | None = None,
    *,
    maxsize: int | None = None,
    typed: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    """Memoize a function with hashable parameters."""

    def _decorator(func: Callable[P, T]) -> _CacheWrapper[P, T]:
        cache: _MaxSizedDict[tuple[Hashable, ...], T] = _MaxSizedDict(maxsize=maxsize)
        cache_get: Callable[[_Key], T | _Sentinel] = lambda k: cache.get(k, _SENTINEL)
        cache_len = cache.__len__
        hits = misses = 0

        def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            nonlocal hits, misses
            key = _make_key(args, kwargs, typed=typed)
            cached_result = cache_get(key)
            if cached_result is _SENTINEL:  # i.e. if not cached.
                misses += 1
                result = func(*args, **kwargs)
                cache[key] = result
                return result
            else:
                hits += 1
                return cast(T, cached_result)

        _wrapper_obj: _CacheWrapper[P, T] = _CacheWrapper(_wrapper)
        _wrapper_obj.cache_info = lambda: CacheInfo(
            hits=hits,
            misses=misses,
            maxsize=maxsize,
            currsize=cache_len(),
        )
        _wrapper_obj.cache = cache
        return _wrapper_obj

    return _decorator if func is None else _decorator(func)


@overload
def lru_cache(
    func: None = None, *, maxsize: int | None = 128, typed: bool = False
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


@overload
def lru_cache(
    func: Callable[P, T], *, maxsize: int | None = 128, typed: bool = False
) -> Callable[P, T]: ...


def lru_cache(
    func: Callable[P, T] | None = None,
    *,
    maxsize: int | None = 128,
    typed: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    """Memoize a function with hashable parameters."""
    return cache(func, maxsize=maxsize, typed=typed)
