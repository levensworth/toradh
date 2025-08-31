import pytest
from toradh import Err, Nothing, Ok, Option, Result, Some

pydantic = pytest.importorskip("pydantic")


def test_option_field_validation_and_serialization() -> None:
    class M(pydantic.BaseModel):
        opt: Option[int]

    m1 = M(opt=Some(10))
    assert isinstance(m1.opt, Some)
    assert m1.opt.unwrap() == 10
    assert m1.model_dump() == {"opt": 10}

    m2 = M(opt=None)
    assert isinstance(m2.opt, Nothing)
    assert m2.model_dump() == {"opt": None}

    m3 = M(opt=10)
    assert isinstance(m3.opt, Some)
    assert m3.opt.unwrap() == 10
    assert m3.model_dump() == {"opt": 10}

    m4 = M(opt=Nothing())
    assert isinstance(m4.opt, Nothing)
    assert m4.model_dump() == {"opt": None}


def test_some_field_validation_and_serialization() -> None:
    class M(pydantic.BaseModel):
        s: Some[int]

    m1 = M(s=Some(3))
    assert isinstance(m1.s, Some)
    assert m1.s.unwrap() == 3
    assert m1.model_dump() == {"s": 3}

    m2 = M(s=3)
    assert isinstance(m2.s, Some)
    assert m2.s.unwrap() == 3
    assert m2.model_dump() == {"s": 3}


def test_nothing_field_validation_and_serialization() -> None:
    class M(pydantic.BaseModel):
        n: Nothing

    m1 = M(n=None)
    assert isinstance(m1.n, Nothing)
    assert m1.model_dump() == {"n": None}

    m2 = M(n=Nothing())
    assert isinstance(m2.n, Nothing)
    assert m2.model_dump() == {"n": None}

    with pytest.raises(pydantic.ValidationError):
        M(n=1)  # type: ignore[arg-type]


def test_ok_field_validation_and_serialization() -> None:
    class M(pydantic.BaseModel):
        ok: Ok[int]

    m1 = M(ok=Ok(7))
    assert isinstance(m1.ok, Ok)
    assert m1.ok.unwrap() == 7
    assert m1.model_dump() == {"ok": 7}

    m2 = M(ok=7)
    assert isinstance(m2.ok, Ok)
    assert m2.ok.unwrap() == 7
    assert m2.model_dump() == {"ok": 7}


def test_err_field_validation_and_no_serialization() -> None:
    class M(pydantic.BaseModel):
        er: Err[ValueError]

    m1 = M(er=Err(ValueError("bad")))
    assert isinstance(m1.er, Err)
    # Err should serialize to None per requirement
    assert m1.model_dump() == {"er": None}

    m2 = M(er=ValueError("oops"))
    assert isinstance(m2.er, Err)
    assert m2.model_dump() == {"er": None}

    with pytest.raises(pydantic.ValidationError):
        M(er="err")  # type: ignore[arg-type]


def test_result_union_ok_and_err() -> None:
    class M(pydantic.BaseModel):
        res: Result[int, Exception]

    m1 = M(res=Ok(11))
    assert isinstance(m1.res, Ok)
    assert m1.model_dump() == {"res": 11}

    m2 = M(res=11)
    assert isinstance(m2.res, Ok)
    assert m2.model_dump() == {"res": 11}

    m3 = M(res=Err(RuntimeError("rt")))
    assert isinstance(m3.res, Err)
    assert m3.model_dump() == {"res": None}


def test_nested_inner_model_serialization() -> None:
    class Inner(pydantic.BaseModel):
        x: int

    class M(pydantic.BaseModel):
        ok: Ok[Inner]
        opt: Option[Inner]

    inner = Inner(x=5)
    m = M(ok=Ok(inner), opt=Some(inner))
    dumped = m.model_dump()
    assert dumped == {"ok": {"x": 5}, "opt": {"x": 5}}
