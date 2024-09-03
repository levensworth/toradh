import typing
from typing import Generic, TypeVar, Union

import typeguard


T = TypeVar("T")
V = TypeVar("V")


class Option(Generic[T]):
    __match_args__ = ("_value",)

    def __init__(self, value: Union[T, None]) -> None:
        """Base Wrapper object to represent an optional value.
        This can be either Some(T) or Nothing().

        ## NOTE:
        Option will not accept a cell to it's constructor. You should use:

        >>> Option.of()

        ### Obs:
        If you desire to use None as a valid value within your program, explicitly
        create an instance as:
        >>> Some(None)

        Args:
            value (Union[T, None]): actual wrapped value.

        Raises:
            ValueError: if calling the __init__ method directly.
        """
        if getattr(self, "_flag", None) is None:
            raise ValueError(
                'you need to call either "empty()" or "of()" methods to create an instance'
            )
        self._value = value

    @classmethod
    def empty(cls) -> "Nothing":
        """Creates an Nothing() instance which represent the absence of a value.

        Returns:
            Nothing:
        """
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
        """Creates a instance of either Some() or Nothing, depending if the value
        if actually None or not.

        Args:
            value (Union[T, None]): value to wrap.

        Returns:
            Union[Some[T], Nothing]: Either an instance of Some[T] if T is not none else Nothing()
        """
        setattr(cls, "_flag", True)
        if value is None:
            return Nothing()
        return Some(value)

    def is_some(self) -> bool:
        """checks if it is an instance of Some[T] or Nothing().

        Returns:
            bool: True if it's an instance of Some() else False.
        """
        return self._value is not None

    def is_nothing(self) -> bool:
        """checks if it is an instance of Some[T] or Nothing().

        Returns:
            bool: True if it's an instance of Nothing() else False.
        """
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
        """Returns the value wrapped in case of Some()
        else returns the default value.

        Args:
            default (T): value to return in case of Nothing()

        Returns:
            T: returned value.
        """
        assert self._value is not None
        return self._value

    @typeguard.typechecked
    def map(self, func: typing.Callable[[T], V]) -> "Option[V]":
        assert self._value
        return Option.of(func(self._value))

    def __repr__(self) -> str:
        return f"Some({self._value})"


class Some(Option[T], Generic[T]):
    __match_args__ = ("_value",)

    def __init__(self, value: T) -> None:
        """Representation of a desired value within a control flow.

        Args:
            value (T): actual value to be wrapped.
        """
        self._flag = True
        super().__init__(value)


class Nothing(Option[None]):
    __match_args__ = ("_value",)

    def __init__(self) -> None:
        """Representation of the absence of a desired value."""
        self._flag = True
        super().__init__(None)

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def unwrap(self) -> typing.NoReturn:
        raise ValueError("Trying to unwrap Nothing() is not allowed")

    @typeguard.typechecked
    def unwrap_or(self, default: T) -> T:
        return default

    @typeguard.typechecked
    def map(self, func: typing.Callable[[T], V]) -> Option[V]:
        return typing.cast(Option, Nothing())

    def __repr__(self) -> str:
        return "Empty"


Optional = typing.Union[Some[T], Nothing]
