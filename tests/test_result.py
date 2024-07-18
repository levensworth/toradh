from dataclasses import dataclass
import datetime
import sys
from toradh import Err, Ok, Result

import pytest

from toradh import is_ok, is_err


@dataclass
class Movie:
    title: str
    director: str
    released: datetime.datetime


@pytest.fixture
def simple_movie() -> Movie:
    return Movie(
        title="the last",
        director="john doe",
        released=datetime.datetime(year=2010, month=8, day=17),
    )


@pytest.fixture
def mock_ok(simple_movie: Movie) -> Ok[Movie]:
    return Ok(simple_movie)


@pytest.fixture
def mock_err() -> Err[ValueError]:
    return Err(ValueError())


def test_map_err(mock_err: Result[Movie, Exception]) -> None:
    if is_err(mock_err):
        new_res = mock_err.map_to_err(KeyError())

        with pytest.raises(KeyError):
            new_res.unwrap()

    else:
        raise AssertionError(f"is_ok return True for {mock_err}")


def test_is_ok(mock_ok: Result[Movie, Exception]) -> None:
    if is_ok(mock_ok):
        assert isinstance(mock_ok, Ok)
    else:
        raise AssertionError(f"is_ok return False for {mock_ok}")


def test_equals(
    mock_err: Result[Movie, Exception], mock_ok: Result[Movie, Exception]
) -> None:
    assert mock_err != mock_ok
    assert mock_ok.is_ok()
    new_movie_ok = Ok(mock_ok.unwrap())
    assert new_movie_ok == mock_ok


def test_kind(mock_ok: Result[Movie, Exception]) -> None:
    assert mock_ok.kind() == mock_ok.unwrap()


if sys.version_info.major == 3 and sys.version_info.minor < 10:
    sys.exit(0)


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
