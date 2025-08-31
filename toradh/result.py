import inspect
import typing
from typing import Any, Callable, Generic, Literal, NoReturn, TypeVar, Union
from typing_extensions import TypeIs

import typeguard

# source: https://jellis18.github.io/post/2021-12-13-python-exceptions-rust-go/

T = TypeVar("T")
V = TypeVar("V")

E = TypeVar("E", bound=BaseException, covariant=True)
R = TypeVar("R", bound=BaseException)


class ResultProto(typing.Protocol[T, E]):
    def __eq__(self, other: Any) -> bool: ...

    def kind(self) -> T:
        """Returns the instance with the objective to be use for structural pattern matching.

        Returns:
            T: wrapped instance
        """
        ...

    def unwrap(self) -> T:
        """Returns the wrapped instance.

        Returns:
            T: instances wrapped by the Ok class.
        """
        ...

    def unwrap_or(self, default: T) -> T:
        """Returns a default object in case the result is of the Err type.

        Args:
            default (T): value to return in case of Err.

        Returns:
            T: either the default value or the unwrapped value.
        """
        ...

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """Given a Err result, call the op callable which should
        help resolve the error.

        Args:
            op (Callable[[E], T]): callable which should return a instance of T
            given an instance of an error.

        Returns:
            T:
        """
        ...

    def is_ok(self) -> bool:
        """Helper function to check if the instance if of type Ok

        Returns:
            bool: True if Ok() instance, else False
        """
        ...

    def is_error(self) -> bool:
        """Helper function to check if the instance if of type Err

        Returns:
            bool: True if Err() instance, else False
        """
        ...

    def if_ok(self, op: Callable[[T], Any]) -> None:
        """invoke the given operation in case of Ok() or else do nothing.

        Args:
            op (Callable[[T], Any]): function to invoke with the content of Ok()
        """
        ...

    async def async_if_ok(self, op: Callable[[T], Any]) -> None:
        """Given a Err result, call the op callable which should
        help resolve the error. Specifically designed for async callables.

        Args:
            op (Callable[[E], T]): callable which should return a instance of T
            given an instance of an error.

        Returns:
            T:
        """
        ...

    def map_to_err(self, result: "Err[R]") -> "Err[R]":
        """Give a new exception to return as a new instance of Err

        Args:
            err (R): Exception to create Err[R]

        Returns:
            Err[R]: New Err[R] instance object.
        """
        ...


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

    def is_ok(self) -> Literal[True]:
        return True

    def is_error(self) -> Literal[False]:
        return False

    def if_ok(self, op: Callable[[T], Any]) -> None:
        """invoke the given operation in case of Ok() or else do nothing.

        Args:
            op (Callable[[T], Any]): function to invoke with the content of Ok()
        """
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

    # Pydantic v2 integration for Ok[T]
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: typing.Any, handler: typing.Any
    ) -> typing.Any:
        try:
            from pydantic_core import core_schema as cs
        except Exception as exc:  # pragma: no cover
            raise exc

        type_args = typing.get_args(source_type)
        inner_type: typing.Any = type_args[0] if type_args else typing.Any
        inner_schema = handler.generate_schema(inner_type)

        def _wrap_validator(value: typing.Any, inner: typing.Any) -> "Ok[typing.Any]":
            if isinstance(value, Ok):
                return typing.cast(Ok[typing.Any], value)
            validated = inner(value)
            return typing.cast(Ok[typing.Any], Ok(validated))

        def _serialize(
            value: "Ok[typing.Any]",
            serializer: typing.Callable[[typing.Any], typing.Any],
        ) -> typing.Any:
            return serializer(value.unwrap())

        python_schema = cs.no_info_wrap_validator_function(
            _wrap_validator, inner_schema
        )
        json_schema = cs.no_info_wrap_validator_function(_wrap_validator, inner_schema)
        ser = cs.wrap_serializer_function_ser_schema(_serialize, schema=inner_schema)
        return cs.json_or_python_schema(
            json_schema=json_schema, python_schema=python_schema, serialization=ser
        )


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
        """Returns the instance with the objective to be use for structural pattern matching.

        Returns:
            E: Instance of the error withhold in the Err object.
        """
        return self._err

    def unwrap(self) -> NoReturn:
        """Unwraps the contained exception

        Raises:
            self._err: raises the exception.

        Returns:
            NoReturn
        """
        raise self._err

    @typeguard.typechecked
    def unwrap_or(self, default: T) -> T:
        return default

    @typeguard.typechecked
    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self._err)

    def is_ok(self) -> Literal[False]:
        return False

    def is_error(self) -> Literal[True]:
        return True

    def if_ok(self, op: Callable[[T], Any]) -> None:
        """invoke the given operation in case of Ok() or else do nothing.

        Args:
            op (Callable[[T], Any]): function to invoke with the content of Ok()
        """
        return None

    async def async_if_ok(self, op: Callable[[T], Any]) -> None:
        """invoke the given an async operation in case of Ok() or else do nothing.

        Args:
            op (Callable[[T], Any]): async function to invoke with the content of Ok()
        """
        return None

    @typeguard.typechecked
    def or_else_throw(self, result: "Err[R]") -> "Err[R]":
        return result

    @typeguard.typechecked
    def map_to_err(self, err: R) -> "Err[R]":
        """Give a new exception to return as a new instance of Err

        Args:
            err (R): Exception to create Err[R]

        Returns:
            Err[R]: New Err[R] instance object.
        """
        return Err(err)

    def __repr__(self) -> str:
        return f"Err({repr(self._err)})"

    # Pydantic v2 integration for Err[E]
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: typing.Any, handler: typing.Any
    ) -> typing.Any:
        try:
            from pydantic_core import core_schema as cs
            from pydantic_core import PydanticCustomError
        except Exception as exc:  # pragma: no cover
            raise exc

        type_args = typing.get_args(source_type)
        err_type: typing.Any = type_args[0] if type_args else BaseException

        # For errors, we accept either an Err[E] instance or a BaseException instance.
        # We cannot reliably validate exception contents; enforce instance check.
        def _plain_validator(value: typing.Any) -> "Err[typing.Any]":
            if isinstance(value, Err):
                return typing.cast(Err[typing.Any], value)
            if isinstance(value, BaseException):
                return typing.cast(Err[typing.Any], Err(value))
            # If type parameter is a specific exception class, allow that
            if isinstance(value, err_type):
                return typing.cast(Err[typing.Any], Err(value))
            raise PydanticCustomError(
                "err_type", "Expected Err[E] or an exception instance"
            )

        def _serialize(value: "Err[typing.Any]") -> typing.Any:
            # Explicitly disallow serialization for Err per requirements
            return None

        python_schema = cs.no_info_plain_validator_function(_plain_validator)
        json_schema = cs.no_info_plain_validator_function(_plain_validator)
        ser = cs.plain_serializer_function_ser_schema(_serialize)
        return cs.json_or_python_schema(
            json_schema=json_schema, python_schema=python_schema, serialization=ser
        )


Result = Union[Ok[T], Err[E]]


# Helper functions


def is_ok(val: Result) -> TypeIs[Ok]:
    """Helper function which indicates if the value is of type Ok or Err

    Args:
        val (Result): Result instance to determine.

    Example:
        >>> x = Err(ValueError())
        >>> if not is_ok(x):
        >>>     # this works because the type checker knows this of type Err
        >>>     x.map_to_err(KeyError())

    Returns:
        TypeIs[Ok]: Returns True if val is Ok else False
    """
    if isinstance(val, Ok):
        return True
    else:
        return False


def is_err(val: Result) -> TypeIs[Err]:
    """Helper function which indicates if the value is of type Err or Ok

    Args:
        val (Result): Result instance to determine.

    Example:
        >>> x = Err(ValueError())
        >>> if is_err(x):
        >>>     # this works because the type checker knows this of type Err
        >>>     x.map_to_err(KeyError())

    Returns:
        TypeIs[Err]: Returns True if val is Err else False
    """
    if isinstance(val, Err):
        return True
    else:
        return False
