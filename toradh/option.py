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
    def of(cls, value: typing.Optional[T]) -> "Optional[T]":
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

    # Pydantic v2 integration
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: typing.Any, handler: typing.Any
    ) -> typing.Any:
        """Provide Pydantic v2 core schema for Option[T].

        Validation behavior:
        - None -> Nothing()
        - Option[T] instance -> passthrough
        - bare value -> validate as T and wrap in Some[T]

        Serialization behavior:
        - Nothing() -> None
        - Some(v) -> v (serialized according to T)
        """
        try:
            from pydantic_core import core_schema as cs
        except (
            Exception
        ) as exc:  # pragma: no cover - only executed if pydantic isn't installed
            raise exc

        type_args = typing.get_args(source_type)
        inner_type: typing.Any = type_args[0] if type_args else typing.Any
        inner_schema = handler.generate_schema(inner_type)

        def _wrap_validator(
            value: typing.Any, inner: typing.Any
        ) -> "Option[typing.Any]":
            if isinstance(value, Option):
                return typing.cast(Option[typing.Any], value)
            if value is None:
                return typing.cast(Option[typing.Any], Nothing())
            validated = inner(value)
            return typing.cast(Option[typing.Any], Some(validated))

        def _serialize(
            value: "Option[typing.Any]",
            serializer: typing.Callable[[typing.Any], typing.Any],
        ) -> typing.Any:
            if isinstance(value, Nothing):
                return None
            # It's Some at this point; delegate to inner serializer
            return serializer(typing.cast(Some[typing.Any], value).unwrap())

        python_schema = cs.no_info_wrap_validator_function(
            _wrap_validator, inner_schema
        )
        json_schema = cs.no_info_wrap_validator_function(_wrap_validator, inner_schema)
        ser = cs.wrap_serializer_function_ser_schema(_serialize, schema=inner_schema)
        return cs.json_or_python_schema(
            json_schema=json_schema, python_schema=python_schema, serialization=ser
        )


class Some(Option[T], Generic[T]):
    __match_args__ = ("_value",)

    def __init__(self, value: T) -> None:
        """Representation of a desired value within a control flow.

        Args:
            value (T): actual value to be wrapped.
        """
        self._flag = True
        super().__init__(value)

    # Pydantic v2 integration for fields typed as Some[T]
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: typing.Any, handler: typing.Any
    ) -> typing.Any:
        try:
            from pydantic_core import core_schema as cs
        except Exception as exc:  # pragma: no cover
            raise exc
        try:
            from pydantic_core import core_schema as cs
        except Exception as exc:  # pragma: no cover
            raise exc

        type_args = typing.get_args(source_type)
        inner_type: typing.Any = type_args[0] if type_args else typing.Any
        inner_schema = handler.generate_schema(inner_type)

        def _wrap_validator(value: typing.Any, inner: typing.Any) -> "Some[typing.Any]":
            if isinstance(value, Some):
                return typing.cast(Some[typing.Any], value)
            # validate bare value as T then wrap
            validated = inner(value)
            return typing.cast(Some[typing.Any], Some(validated))

        def _serialize(
            value: "Some[typing.Any]",
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

    # Pydantic v2 integration for fields typed as Nothing
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: typing.Any, handler: typing.Any
    ) -> typing.Any:
        try:
            from pydantic_core import core_schema as cs
            from pydantic_core import PydanticCustomError
        except Exception as exc:  # pragma: no cover
            raise exc

        def _plain_validator(value: typing.Any) -> "Nothing":
            if isinstance(value, Nothing):
                return value
            if value is None:
                return Nothing()
            raise PydanticCustomError("nothing_type", "Expected None for Nothing()")

        def _serialize(value: "Nothing") -> typing.Any:
            return None

        python_schema = cs.no_info_plain_validator_function(_plain_validator)
        json_schema = cs.no_info_plain_validator_function(_plain_validator)
        ser = cs.plain_serializer_function_ser_schema(_serialize)
        return cs.json_or_python_schema(
            json_schema=json_schema, python_schema=python_schema, serialization=ser
        )


Optional = typing.Union[Some[T], Nothing]
