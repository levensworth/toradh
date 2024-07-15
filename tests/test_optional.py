import sys
import pytest
from toradh.result import Option, Nothing, Some


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


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
def test_match() -> None:
    option = Option.of(1)

    match option:
        case Nothing():
            raise AssertionError()
        case Some(val):
            assert val == 1


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
def test_match_with_none() -> None:
    option = Some(None)

    match option:
        case Nothing():
            raise AssertionError()
        case Some(None):
            pass
        case Some(int()):
            raise ValueError()
