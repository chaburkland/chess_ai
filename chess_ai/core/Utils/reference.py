from typing import Generic, TypeVar


T = TypeVar('T')

class Ref(Generic[T]):
    def __init__(self, value):
        self._value: Generic[T] = value

    @property
    def value(self) -> Generic[T]:
        return self._value

    def update(self, value: Generic[T]):
        self._value = value

    def __call__(self) -> Generic[T]:
        return self.value

    def __eq__(self, other: Generic[T]):
        return self.value == other.value

    def __repr__(self) -> str:
        return f'Ref<{self._value.__class__.__name__}, {self._value}>'
