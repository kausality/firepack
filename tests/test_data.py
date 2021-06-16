import pytest
import json
from firepack.errors import MultiValidationError, ParamError
from firepack.fields import IntField, StrField, ListField
from firepack.data import FireData


def test_validation_errors():
    # Given: required field
    class Foo(FireData):
        a = IntField(required=True)

    # When: no value is initialized
    f = Foo()

    # Then: raise errors
    with pytest.raises(MultiValidationError):
        f.to_json()

    with pytest.raises(MultiValidationError):
        f.to_dict()


def test_valid_to_dict():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)
        b = StrField(required=True)

    f = Foo()

    # When: valid inputs given
    f.a = 1
    f.b = 'foo'

    # Then: valid conversion to dict
    val = {'a': 1, 'b': 'foo'}
    assert f.to_dict() == val


def test_valid_to_json():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)
        b = StrField(required=True)

    # When: valid inputs given
    f = Foo()
    f.a = 1
    f.b = 'foo'

    # Then: valid conversion to json
    val = {'a': 1, 'b': 'foo'}
    assert f.to_json() == json.dumps(val)


def test_nested_valid_conversion():
    # Given: nested data classes
    class Foo(FireData):
        a = IntField(required=True)

    class Bar(FireData):
        a = IntField(required=True)
        b = Foo()

    class Baz(FireData):
        c = ListField(IntField())
        d = Bar()

    # When: valid init done
    foo = Foo()
    foo.a = 1

    bar = Bar()
    bar.a = 1
    bar.b = foo

    baz = Baz()
    baz.c = [1, 2, 3]
    baz.d = bar

    # Then: valid conversion to dict/json along with nested fields
    val = {'c': [1, 2, 3], 'd': {'a': 1, 'b': {'a': 1}}}
    assert baz.to_dict() == val
    assert baz.to_json() == json.dumps(val)


def test_nested_invalid_input_raises_error():
    # Given: nested data classes
    class Foo(FireData):
        a = IntField(required=True)

    class Bar(FireData):
        a = IntField(required=True)
        b = Foo()

    # When: invalid init done
    foo = Foo()
    foo.a = 'a'

    bar = Bar()
    bar.a = 1
    bar.b = foo

    # Then: raise error
    with pytest.raises(MultiValidationError):
        bar.validate()


def test_from_dict():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: valid input given
    val = {'a': 1}
    obj = Foo.from_dict(val)

    # Then: init fields
    assert obj.a == 1


def test_from_dict_invalid_input_raises_error():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: invalid input type given
    input_val = 'a'

    # Then: raise error
    with pytest.raises(AssertionError):
        Foo.from_dict(input_val)


def test_from_dict_unknown_field_when_exact_raises_error():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: unknown input value given
    val = {'a': 1, 'b': 1}

    # Then: raise error
    with pytest.raises(ParamError):
        Foo.from_dict(val)


def test_from_dict_unknown_field_when_not_exact_not_raises_error():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: unknown input value given
    val = {'a': 1, 'b': 1}

    # Then: not raise error
    try:
        Foo.from_dict(val, exact=False)
    except ParamError:
        pytest.fail('Should not raise ParamError')


def test_from_json():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: valid input json given
    val = {'a': 1}
    obj = Foo.from_json(json.dumps(val))

    # Then: init fields
    assert obj.a == 1


def test_from_json_invalid_input_raises_error():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: non json input given
    input_val = {
        'a': 1
    }

    # Then: raise error
    with pytest.raises(AssertionError):
        Foo.from_json(input_val)


def test_from_json_unknown_field_when_exact_raises_error():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: unknown input value given
    val = {'a': 1, 'b': 1}

    # Then: raise error
    with pytest.raises(ParamError):
        Foo.from_json(json.dumps(val), exact=True)


def test_from_json_unknown_field_when_not_exact_not_raises_error():
    # Given: data
    class Foo(FireData):
        a = IntField(required=True)

    # When: unknown input value given
    val = {'a': 1, 'b': 1}

    # Then: not raise error
    try:
        Foo.from_json(json.dumps(val), exact=False)
    except ParamError:
        pytest.fail('Should not raise ParamError')


def test_inheritance():
    # Given: inherited data class
    class Foo(FireData):
        a = IntField()

    class Bar(Foo):
        b = IntField()

    # When: init using child class
    bar = Bar()
    bar.a = 1
    bar.b = 2

    # Then: have parent's field too
    val = {'a': 1, 'b': 2}
    assert bar.to_dict() == val


def test_invalid_default_value_raises_error():
    # Given: given invalid default value
    class Foo(FireData):
        a = IntField(default='a')

    # When: init without supplying any other value
    foo = Foo()

    # Then: throw error
    with pytest.raises(MultiValidationError):
        foo.validate()


def test_returns_default_value():
    # Given: valid default value given
    class Foo(FireData):
        a = IntField(default=1)

    # When: init without supplying any other value
    foo = Foo()

    # Then: return value and successfully validate without any errors
    assert foo.a == 1
    foo.validate()




