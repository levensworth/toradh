import pathlib
import sys
from mktestdocs import check_md_file  # type: ignore
import pytest


# Note the use of `str`, makes for pretty output
@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
@pytest.mark.parametrize("fpath", pathlib.Path("docs").glob("**/*.md"), ids=str)
def test_docs(fpath):
    check_md_file(fpath=fpath)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10 or higher")
@pytest.mark.parametrize(
    "fpath",
    pathlib.Path(".").glob("readme.md"),
    ids=str,
)
def test_readme(fpath):
    check_md_file(fpath=fpath)
