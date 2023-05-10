from typing import Generic, Union, TypeVar

# Rust Like Error Handling, SAY NO TO EXCEPTION"
T = TypeVar("T")
E = TypeVar("E")


class Ok(Generic[T, E]):
    _value: T
    __match_args__ = ("_value",)

    def __init__(self, value: T) -> None:
        self._value = value

    def is_ok(self):
        return True

    def is_err(self):
        return False

    def unwrap(self):
        return self._value


class Err(Generic[T, E]):
    _err: E
    __match_args__ = ("_err",)

    def __init__(self, value: E) -> None:
        self._value = value

    def is_ok(self):
        return False

    def is_err(self):
        return True

    def unwrap(self):
        return self._value


Result = Union[Ok[T, E], Err[T, E]]
