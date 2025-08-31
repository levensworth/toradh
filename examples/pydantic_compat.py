from pydantic import BaseModel
from toradh import Option, Some, Nothing, Ok, Err, Result


class Inner(BaseModel):
    x: int


class MyModel(BaseModel):
    opt: Option[int]
    ok: Ok[Inner]
    res: Result[int, Exception]


def main() -> None:
    m = MyModel(opt=Some(1), ok=Ok(Inner(x=5)), res=Ok(10))
    print("m:", m)
    print("m.model_dump():", m.model_dump())

    # Intentionally pass bare values to demonstrate Pydantic wrapping
    m2 = MyModel(opt=None, ok={"x": 7}, res=5)  # type: ignore[arg-type]
    print("m2:", m2)
    print("m2.model_dump():", m2.model_dump())

    m3 = MyModel(opt=Nothing(), ok=Ok(Inner(x=1)), res=Err(RuntimeError("boom")))  # type: ignore[arg-type]
    print("m3:", m3)
    print("m3.model_dump():", m3.model_dump())


if __name__ == "__main__":
    main()
