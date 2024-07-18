from dataclasses import dataclass
import datetime
import sys

import pytest

from toradh.result import Err, Ok


def pytest_configure(config):
    if sys.version_info < (3, 10):
        # Skip test files requiring Python 3.10+
        config.addinivalue_line("markers", "skipif: skip tests requiring Python 3.10+")


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
