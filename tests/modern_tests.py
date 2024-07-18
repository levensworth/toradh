import sys

import pytest

from tests.conftest import Movie
from toradh import Option, Result, Err, Ok, Some, Nothing


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


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
def test_match_over_ok(mock_ok: Result[Movie, Exception]) -> None:
    if sys.version_info < (3, 10):
        pytest.skip("requires Python 3.10 or higher")

    unwrapped = None
    match mock_ok:
        case Ok(Movie()):
            unwrapped = mock_ok.unwrap()
        case Err():
            raise AssertionError("match an error when an Ok value was expected")

    assert unwrapped == mock_ok.unwrap()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
def test_match_over_err(mock_err: Result[Movie, Exception]) -> None:
    if sys.version_info < (3, 10):
        pytest.skip("requires Python 3.10 or higher")

    with pytest.raises(ValueError):
        match mock_err:
            case Ok(Movie()):
                raise AssertionError("match an Ok when an Err value was expected")
            case Err(ValueError()):
                mock_err.unwrap()
            case Err(KeyError()):
                raise AssertionError("match a KeyError when ValueError was expected")
