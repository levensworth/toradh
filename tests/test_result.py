from tests.conftest import Movie
from toradh import Ok, Result

import pytest

from toradh import is_ok, is_err


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
