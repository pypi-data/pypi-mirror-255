from pydantic_dbmodel_core import DbModelCore


def test_class():
    class MyDbModel(DbModelCore):
        var1: str
        var2: str

        @classmethod
        def __pydantic_init_subclass__(cls):
            for field in cls.model_fields:
                setattr(cls, field, f"{field} CLASS VALUE")

    class MyClass(MyDbModel):
        var3: str
        var4: str

    assert MyClass.var1 == "var1 CLASS VALUE"
    assert MyClass.var2 == "var2 CLASS VALUE"
    assert MyClass.var3 == "var3 CLASS VALUE"
    assert MyClass.var4 == "var4 CLASS VALUE"

    obj = MyClass(
        var1="var1 INSTANCE VALUE",
        var2="var2 INSTANCE VALUE",
        var3="var3 INSTANCE VALUE",
        var4="var4 INSTANCE VALUE",
    )

    assert obj.var1 == "var1 INSTANCE VALUE"
    assert obj.var2 == "var2 INSTANCE VALUE"
    assert obj.var3 == "var3 INSTANCE VALUE"
    assert obj.var4 == "var4 INSTANCE VALUE"
    assert MyClass.var1 == "var1 CLASS VALUE"
    assert MyClass.var2 == "var2 CLASS VALUE"
    assert MyClass.var3 == "var3 CLASS VALUE"
    assert MyClass.var4 == "var4 CLASS VALUE"
