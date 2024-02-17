import threading
from abc import abstractmethod
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class Provider(Generic[T]):
    def __init__(self, initializer: Callable[..., T], *initializer_args, **initializer_kwargs) -> None:
        self._initializer = initializer
        self._initializer_kwargs = initializer_kwargs
        self._initializer_args = initializer_args

    @abstractmethod
    def get(self) -> T:
        pass


class GenericProvider(Provider[T]):
    def __init__(self, initializer: Callable[..., T], *initializer_args, **initializer_kwargs) -> None:
        super().__init__(initializer, *initializer_args, **initializer_kwargs)
        self._value: Optional[T] = None

    def get(self) -> T:
        if self._value is None:
            self._value = self._initializer(*self._initializer_args, **self._initializer_kwargs)

        return self._value


class ThreadProvider(Provider[T]):
    def __init__(self, initializer: Callable[..., T], *initializer_args, **initializer_kwargs) -> None:
        super().__init__(initializer, *initializer_args, **initializer_kwargs)
        self._tls = threading.local()

    def get(self) -> T:
        if not hasattr(self._tls, "value"):
            self._tls.value = self._initializer(*self._initializer_args, **self._initializer_kwargs)

        return self._tls.value
