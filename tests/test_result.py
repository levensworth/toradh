from dataclasses import dataclass
import datetime
import sys
from toradh.result import Err, Ok, Result

import pytest


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


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
def test_match_over_ok(mock_ok: Result[Movie, Exception]) -> None:
    unwrapped = None
    match mock_ok:
        case Ok(Movie()):
            unwrapped = mock_ok.unwrap()
        case Err():
            raise AssertionError("match an error when an Ok value was expected")

    assert unwrapped == mock_ok.unwrap()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
def test_match_over_err(mock_err: Result[Movie, Exception]) -> None:
    with pytest.raises(ValueError):
        match mock_err:
            case Ok(Movie()):
                raise AssertionError("match an Ok when an Err value was expected")
            case Err(ValueError()):
                mock_err.unwrap()
            case Err(KeyError()):
                raise AssertionError("match a KeyError when ValueError was expected")

                
