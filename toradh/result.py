import inspect
import typing
from typing import Any, Callable, Generic, NoReturn, TypeVar, Union

import typeguard

# source: https://jellis18.github.io/post/2021-12-13-python-exceptions-rust-go/

T = TypeVar("T")
V = TypeVar("V")

E = TypeVar("E", bound=BaseException, covariant=True)
R = TypeVar("R", bound=BaseException)


class ResultProto(typing.Protocol[T, E]):
    def __eq__(self, other: Any) -> bool: ...

    def kind(self) -> T: ...

    def unwrap(self) -> T: ...

    def unwrap_or(self, default: T) -> T: ...

    def unwrap_or_else(self, op: Callable[[E], T]) -> T: ...

    def is_ok(self) -> bool: ...

    def is_error(self) -> bool: ...

    def if_ok(self, op: Callable[[T], Any]) -> None: ...

    async def async_if_ok(self, op: Callable[[T], Any]) -> None: ...

    def map_to_err(self, result: "Err[R]") -> "Err[R]": ...


class Ok(Generic[T]):
    _value: T
    __match_args__ = ("_value",)

    def __init__(self, value: T):
        """Creates a OK object which represent a successful value.

        Args:
            value (T): instance to wrap
        """
        self._value = value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Ok):
            return self._value == other._value
        return False

    def kind(self) -> T:
        """Returns the instance with the objective to be use for structural pattern matching.

        Returns:
            T: wrapped instance
        """
        return self._value

    def unwrap(self) -> T:
        """Returns the wrapped instance.

        Returns:
            T: instances wrapped by the Ok class.
        """
        return self._value

    def unwrap_or(self, default: T) -> T:
        """Returns a default object in case the result is of the Err type.

        Args:
            default (T): value to return in case of Err.

        Returns:
            T: either the default value or the unwrapped value.
        """
        return self.unwrap()

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """Given a Err result, call the op callable which should
        help resolve the error.

        Args:
            op (Callable[[E], T]): callable which should return a instance of T
            given an instance of an error.

        Returns:
            T:
        """
        return self.unwrap()

    def is_ok(self) -> bool:
        return True

    def is_error(self) -> bool:
        return False

    def if_ok(self, op: Callable[[T], Any]) -> None:
        op(self.unwrap())

    async def async_if_ok(self, op: Callable[[T], Any]) -> None:
        """Given a Err result, call the op callable which should
        help resolve the error. Specifically designed for async callables.

        Args:
            op (Callable[[E], T]): callable which should return a instance of T
            given an instance of an error.

        Returns:
            T:
        """
        res = op(self.unwrap())
        if inspect.isawaitable(res):
            await res

    def or_else_throw(self, result: "Err[R]") -> "Ok[T]":
        return Ok(self.unwrap())

    def __repr__(self) -> str:
        return f"Ok({repr(self._value)})"


class Err(Generic[E]):
    _err: E
    __match_args__ = ("_err",)

    def __init__(self, err: E):
        """Representation of an wrapped error. Meant to be use for control flow
        management.

        Args:
            err (E): error instance to wrap
        """
        self._err = err

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Err):
            return self._err == other._err
        return False

    def kind(self) -> E:
        return self._err

    def unwrap(self) -> NoReturn:
        raise self._err

    @typeguard.typechecked
    def unwrap_or(self, default: T) -> T:
        return default

    @typeguard.typechecked
    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self._err)

    def is_ok(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    def if_ok(self, op: Callable[[T], Any]) -> None:
        return None

    async def async_if_ok(self, op: Callable[[T], Any]) -> None:
        return None

    @typeguard.typechecked
    def or_else_throw(self, result: "Err[R]") -> "Err[R]":
        return result

    @typeguard.typechecked
    def map_to_err(self, err: R) -> "Err[R]":
        return Err(err)

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"


Result = Union[Ok[T], Err[E]]


class Option(Generic[T]):
    __match_args__ = ("_value",)

    def __init__(self, value: Union[T, None]):
        if getattr(self, "_flag", None) is None:
            raise ValueError(
                'you need to call either "empty()" or "of()" methods to create an instance'
            )
        self._value = value

    @classmethod
    def empty(cls) -> "Nothing":
        setattr(cls, "_flag", True)
        return Nothing()

    @typing.overload
    @classmethod
    def of(cls, value: T) -> "Some[T]": ...

    @typing.overload
    @classmethod
    def of(cls, value: None) -> "Nothing": ...

    @classmethod
    def of(cls, value: typing.Optional[T]) -> Union["Some[T]", "Nothing"]:
        setattr(cls, "_flag", True)
        if value is None:
            return Nothing()
        return Some(value)

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None

    @typeguard.typechecked
    def unwrap(self) -> T:
        """Returns the value wrapped in the Option
        Returns:
            T: value wrapped.
        """
        assert self._value is not None
        return self._value

    @typeguard.typechecked
    def unwrap_or(self, default: T) -> T:
        assert self._value is not None
        return self._value

    @typeguard.typechecked
    def map(self, func: typing.Callable[[T], R]) -> "Option[R]":
        assert self._value
        return Option.of(func(self._value))

    def __repr__(self) -> str:
        return f"Some({self._value})"


class Some(Option[T], Generic[T]):
    __match_args__ = ("_value",)

    def __init__(self, value: T):
        self._flag = True
        super().__init__(value)


class Nothing(Option[None]):
    __match_args__ = ("_value",)

    def __init__(self):
        self._flag = True
        super().__init__(None)

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def unwrap(self) -> None:
        return None

    @typeguard.typechecked
    def unwrap_or(self, default: T) -> T:
        return default

    @typeguard.typechecked
    def map(self, func: typing.Callable[[T], R]) -> Option[R]:
        return typing.cast(Option, Nothing())

    def __repr__(self) -> str:
        return "Empty"
