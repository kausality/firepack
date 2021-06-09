import pytest
from functools import wraps
from firepack.service import FireService
from firepack.fields import IntField
from firepack.errors import *


class RecordExec:
    """Utility to record execution of Service class methods and capture arguments
    """

    def record(self, func):
        @wraps(func)
        def _record(obj, *args, **kwargs):
            value = {'_args': args, **kwargs}
            setattr(self, func.__name__, value)
            return func(obj, *args, **kwargs)

        return _record

    def __getattr__(self, name):
        return self.__dict__.get(name)


def test_validation_error():
    recorder = RecordExec()

    # Given: a service class with field constraints
    class Service(FireService):
        a = IntField(min_value=1)
        b = IntField(min_value=2)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass

    s = Service()

    # When: given input not matching constraints
    input_dict = {
            'a': 0,
            'b': 1
    }

    # Then: raise error
    with pytest.raises(MultiValidationError) as ex:
        s.call(input_dict)
        assert len(ex.errors) == 2
        assert all([isinstance(e, ValidationError) for e in ex.errors])
    assert recorder.pre_fire is None
    assert recorder.fire is None
    assert recorder.post_fire is None


def test_skip_error():
    recorder = RecordExec()

    # Given: service class which skips execution
    class Service(FireService):
        a = IntField(required=True)

        @recorder.record
        def pre_fire(self):
            raise SkipError()

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass

    s = Service()
    # When: service called
    s.call({
        'a': 10
    })

    # Then: does not run fire()
    assert recorder.pre_fire is not None
    assert recorder.fire is None
    assert recorder.post_fire is not None
    args = recorder.post_fire['_args']
    assert args[0] is False
    assert isinstance(args[1], SkipError)


def test_successful_execution():
    recorder = RecordExec()

    # Given: service class
    class Service(FireService):
        a = IntField(required=True)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass

    s = Service()
    # When: called with valid input
    s.call({
        'a': 10
    })

    # Then: completes execution
    assert recorder.pre_fire is not None
    assert recorder.fire is not None
    assert recorder.post_fire is not None
    args = recorder.post_fire['_args']
    assert args[0] is True
    assert args[1] is None


def test_multiple_service_instances_have_different_field_values():
    # Given: a service
    class Service(FireService):
        a = IntField(required=True)

        def pre_fire(self):
            pass

        def fire(self, **kwargs):
            pass

        def post_fire(self, fired, exc):
            pass

    # When: creating different service instants with different values
    s1 = Service()
    s2 = Service()
    s1.call({
        'a': 10
    })
    s2.call({
        'a': 20
    })

    # Then: each service instant should preserve its own value
    assert s1.a == 10
    assert s2.a == 20


def test_runs_successfully_when_no_defined_fields():
    recorder = RecordExec()

    # Given: service class with no declared input fields
    class Service(FireService):
        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass

    # When: no input value given
    input_dict = {}
    s = Service()
    s.call(input_dict)

    # Then: completes execution
    assert recorder.pre_fire is not None
    assert recorder.fire is not None
    assert recorder.post_fire is not None


def test_missing_required_input_field_raises_error():
    recorder = RecordExec()

    # Given: a service with required input field
    class Service(FireService):
        a = IntField(required=True)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass

    # When: no input value given
    input_dict = {}

    # Then: raise error
    s = Service()
    with pytest.raises(MultiValidationError):
        s.call(input_dict)

    assert recorder.pre_fire is None
    assert recorder.fire is None
    assert recorder.post_fire is None


def test_unknown_input_field_when_exact_raises_error():
    recorder = RecordExec()

    # Given: service with only one input field
    class Service(FireService):
        a = IntField(required=True)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass

    s = Service()

    # When: passed defined field and one undeclared input field with no exact matching
    input_dict = {
        'a': 0,
        'b': 1
    }

    # Then: raise error
    with pytest.raises(ParamError):
        s.call(input_dict, exact=True)
    assert recorder.pre_fire is None
    assert recorder.fire is None
    assert recorder.post_fire is None


def test_unknown_input_field_when_not_exact_not_raises_error():
    recorder = RecordExec()

    # Given: service with only one input field
    class Service(FireService):
        a = IntField(required=True)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass

    # When: passed defined field and one undeclared input field
    input_dict = {
        'a': 0,
        'b': 1
    }

    # Then: raise no error
    s = Service()
    s.call(input_dict, exact=False)
    assert recorder.pre_fire is not None
    assert recorder.fire is not None
    assert recorder.post_fire is not None



