from firepack.fields import IntField
from firepack.data import FireData


class FooData(FireData):
    a = IntField(required=True, min_value=1)


class BarData(FireData):
    a = IntField()
    b = FooData()  # nested reference to data object


f = FooData()
f. a = 1

b = BarData()
b.a = 2
b.b = f

ret = b.to_dict()
print(ret)  # {'a': 2, 'b': {'a': 1}}
