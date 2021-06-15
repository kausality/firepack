import pytest
from firepack.validators import *
from firepack.fields import *
from firepack.errors import ValidationError
from firepack.data import FireData

FIELD_NAME = 'a'


def init_field_holder(field_instance):
    class FieldHolder:
        a = field_instance

    return FieldHolder()


class Data(FireData):
    a = IntField(required=True)
    b = IntField(required=True)


@pytest.mark.parametrize('field, value', [
    (BoolField(), 1),
    (CharField(), 1),
    (StrField(), 1),
    (NumericField(), 'a'),
    (IntField(), 1.5),
    (FloatField(), 1),
    (DateField(), datetime.now()),
    (DateTimeField(), datetime.now().date()),
    (DictField(), []),
    (EmailField(), 'aaa.com'),
    (FireDataField(Data), 'a'),
    (ListField(StrField()), {})
])
def test_default_validation_raises_error(field, value):
    # Given: required is True
    fh = init_field_holder(field)

    # When: init with invalid value type
    setattr(fh, FIELD_NAME, value)

    # Then: raise error
    with pytest.raises(ValidationError):
        field._run_validation(value)


@pytest.mark.parametrize('field', [
    BoolField(required=True),
    CharField(required=True),
    StrField(required=True),
    NumericField(required=True),
    IntField(required=True),
    FloatField(required=True),
    DateField(required=True),
    DateTimeField(required=True),
    DictField(required=True),
    EmailField(required=True),
    FireDataField(Data, required=True),
    ListField(StrField(required=True), required=True)
])
def test_required_field_empty_raises_error(field):
    # Given: required is True
    fh = init_field_holder(field)

    # When: value is None
    setattr(fh, FIELD_NAME, None)

    # Then: raise error
    with pytest.raises(ValidationError):
        field._run_validation(None)


@pytest.mark.parametrize('field, value', [
    (BoolField(), True),
    (CharField(), 'a'),
    (StrField(), 'aaa'),
    (NumericField(), 1),
    (NumericField(), 1.0),
    (IntField(), 1),
    (FloatField(), 1.5),
    (DateField(), datetime.now().date()),
    (DateTimeField(), datetime.now()),
    (DictField(), {}),
    (EmailField(), 'aaa@aaa.com'),
    (ListField(StrField()), ['aaa'])
])
def test_returns_valid_value(field, value):
    # Given: required is True
    fh = init_field_holder(field)

    # When: init with valid value
    setattr(fh, FIELD_NAME, value)

    # Then: return value
    assert getattr(fh, FIELD_NAME) == value


@pytest.mark.parametrize('field', [
    BoolField(default=True),
    CharField(default='a'),
    StrField(default='aaa'),
    NumericField(default=1.0),
    IntField(default=1),
    FloatField(default=1.5),
    DateField(default=datetime.now().date()),
    DateTimeField(default=datetime.now()),
    DictField(default={}),
    EmailField(default='aaa@aaa.com'),
    ListField(StrField(), default=['aaa'])
])
def test_returns_default_value(field):
    # Given: required is True and default is provided
    fh = init_field_holder(field)

    # When: value is None
    setattr(fh, FIELD_NAME, None)

    # Then: return default value
    assert getattr(fh, FIELD_NAME) == field.options['default']


@pytest.mark.parametrize('field', [
    BoolField(required=False),
    CharField(required=False),
    StrField(required=False),
    NumericField(required=False),
    IntField(required=False),
    FloatField(required=False),
    DateField(required=False),
    DateTimeField(required=False),
    DictField(required=False),
    EmailField(required=False),
    ListField(StrField(required=False), required=False)
])
def test_returns_none_when_value_not_required(field):
    # Given: required is False
    fh = init_field_holder(field)

    # When: value is None
    setattr(fh, FIELD_NAME, None)

    # Then: return None
    assert getattr(fh, FIELD_NAME) is None


def always_error_validator(name, value):
    raise ValidationError(name, '')


@pytest.mark.parametrize('field, value', [
    (BoolField(validators=[always_error_validator]), True),
    (CharField(validators=[always_error_validator]), 'a'),
    (StrField(validators=[always_error_validator]), 'aa'),
    (NumericField(validators=[always_error_validator]), 1),
    (IntField(validators=[always_error_validator]), 1),
    (FloatField(validators=[always_error_validator]), 1.0),
    (DateField(validators=[always_error_validator]), datetime.now().date()),
    (DateTimeField(validators=[always_error_validator]), datetime.now()),
    (DictField(validators=[always_error_validator]), {}),
    (EmailField(validators=[always_error_validator]), 'test@example.com'),
    (ListField(StrField(), validators=[always_error_validator]), ['a', 'b', 'c'])
])
def test_custom_validation_raises_error(field, value):
    # Given: field with custom validator
    fh = init_field_holder(field)

    # When: using a valid value
    setattr(fh, FIELD_NAME, value)

    # Then: raise error because of custom validator
    with pytest.raises(ValidationError):
        field._run_validation(value)


@pytest.mark.parametrize('field, value', [
    (NumericField(validators=[interval(min_value=0)]), -1),
    (IntField(validators=[interval(min_value=0)]), -1),
    (FloatField(validators=[interval(min_value=2.0)]), 1.0)
])
def test_min_value_violation_raises_error(field, value):
    # Given: min option
    fh = init_field_holder(field)

    # When: value less than min
    setattr(fh, FIELD_NAME, value)

    # Then: raise error
    with pytest.raises(ValidationError):
        field._run_validation(value)


@pytest.mark.parametrize('field, value', [
    (NumericField(validators=[interval(max_value=1)]), 2),
    (IntField(validators=[interval(max_value=1)]), 2),
    (FloatField(validators=[interval(max_value=1.0)]), 2.0)
])
def test_max_value_violation_raises_error(field, value):
    # Given: max option
    fh = init_field_holder(field)

    # When: value greater than max
    setattr(fh, FIELD_NAME, value)

    # Then: raise error
    with pytest.raises(ValidationError):
        field._run_validation(value)


@pytest.mark.parametrize('field, value', [
    (StrField(validators=[length(min_length=2)]), 'a'),
    (ListField(IntField(), validators=[length(min_length=2)]), [1])
])
def test_min_length_violation_raises_error(field, value):
    # Given: min_length option
    fh = init_field_holder(field)

    # When: value length less than min_length
    setattr(fh, FIELD_NAME, value)

    # Then: raise error
    with pytest.raises(ValidationError):
        field._run_validation(value)


@pytest.mark.parametrize('field, value', [
    (StrField(validators=[length(max_length=2)]), 'aaa'),
    (ListField(IntField(), validators=[length(max_length=2)]), [1, 2, 3])
])
def test_max_length_violation_raises_error(field, value):
    # Given: max_length option
    fh = init_field_holder(field)

    # When: value length greater than max_length
    setattr(fh, FIELD_NAME, value)

    # Then: raise error
    with pytest.raises(ValidationError):
        field._run_validation(value)


@pytest.mark.parametrize('field, value', [
    (ListField(ListField(IntField())), [[1, 2], [3, 4]]),
    (ListField(ListField(ListField(IntField()))), [[[1, 2], [3, 4]], [[[5, 6], [7, 8]]]])
])
def test_nested_list(field, value):
    # Given: field with nested list field
    fh = init_field_holder(field)

    # When: initialize with nested list value
    setattr(fh, FIELD_NAME, value)

    # Then: return the value
    assert getattr(fh, FIELD_NAME) == value


@pytest.mark.parametrize('field, value', [
    (ListField(ListField(IntField(max_value=0))), [[1, 2], [3, 4]]),
    # extra nested list value
    (ListField(ListField(IntField())), [[[1, 2], [3, 4]], [[[5, 6], [7, 8]]]]),  
    (ListField(ListField(ListField(IntField(), min_length=3))), [[[1, 2], [3, 4]], [[[5, 6], [7, 8]]]]),
    (ListField(ListField(StrField(min_length=3))), [['aaaa', 'bbb'], ['c', 'd']])
])
def test_nested_list_violation_raises_error(field, value):
    # Given: field with nested list field
    fh = init_field_holder(field)

    # When: initialize with nested list value violating validation
    setattr(fh, FIELD_NAME, value)

    # Then: raise error
    with pytest.raises(ValidationError):
        field._run_validation(value)


def test_firedatafield_returns_valid_value():
    # Given: a firedatafield
    field = FireDataField(Data)
    fh = init_field_holder(field)

    # When: init with value
    d = Data()
    d.a = 100
    setattr(fh, FIELD_NAME, d)

    # Then: return that firedatafield instance
    assert getattr(fh, FIELD_NAME) == d


def test_firedatafield_inside_listfield_returns_valid_value():
    # Given: firedatafield inside listfield
    field = ListField(FireDataField(Data))
    fh = init_field_holder(field)

    # When: init
    d = Data()
    d.a = 100
    value = [d]
    setattr(fh, FIELD_NAME, value)

    # Then: return list containing firedatafield instance
    ret = getattr(fh, FIELD_NAME)
    assert ret == value
    assert ret[0] == d


def test_firedatafield_inside_listfield_returns_default_value():
    # Given: listfield with default value
    d = Data()
    d.a = 100
    field = ListField(FireDataField(Data, required=True), default=[d])
    fh = init_field_holder(field)

    # When: init
    setattr(fh, FIELD_NAME, None)

    # Then: return list containing firedatafield
    ret = getattr(fh, FIELD_NAME)
    assert getattr(fh, FIELD_NAME) == [d]
    assert ret[0] == d

