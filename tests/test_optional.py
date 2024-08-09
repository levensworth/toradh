import pytest

from toradh import Option, Nothing


@pytest.fixture
def empty_option() -> Nothing:
    return Option.empty()


@pytest.fixture
def full_option() -> Option[str]:
    return Option.of("")


def test_empty_option_is_none(empty_option: Nothing) -> None:
    assert empty_option.is_none()


def test_empty_unwrap_or(empty_option: Nothing) -> None:
    val = ""
    assert empty_option.unwrap_or(val) == val


def test_option_unwrap(full_option: Option) -> None:
    assert full_option.unwrap() == ""


def test_of_none() -> None:
    option = Option.of(None)
    assert isinstance(option, Nothing)


def test_of_something() -> None:
    option = Option.of(1)
    assert isinstance(option, Option)
    assert option.is_some()


def test_dataclass_optional() -> None:
    from dataclasses import dataclass

    @dataclass
    class User:
        name: Option[str]

    user = User(name=Option.of("a"))
    assert user.name.is_some()
