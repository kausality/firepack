import re
import numbers
from datetime import date, datetime
from firepack import validators
from firepack.errors import SkipError, ValidationError

_null = object()


class Field:
    """Base class for all `Field` types.
    
    Raises:
        ValidationError: Raised when `Field` value fails validation.
    """ 
    def __init__(self, required=True, default=_null, validators=[], **options):
        """
        Args:
            required (object, optional): Determine whether a value for `Field` is required.
            default (object, optional): Instantiate `Field` with this default value.
            validators (list, optional): A list of validators to apply. 
            Validators are functions with signature: `validator(name, value)` where `name` is `Field` attribute name and `value` is the provided value.
        """
        self.options = {}
        """The keyword arguments provided to `Field`.
        """
        self.name = None
        """The name of the `Field` attribute.
        """
        self.options['required'] = required
        self.options['default'] = default
        self.options['validators'] = validators
        self.options.update(**options)

    def __set_name__(self, owner, name):
        self.name = name
        """The name of the attribute to which this `Field` instance is assigned.
        """

    def __get__(self, instance, instance_type):
        value = instance.__dict__.get(self.name)
        if value is _null:
            return None
        return value

    def __set__(self, instance, value):
        if value is None:
            value = self.options['default']
        instance.__dict__[self.name] = value

    def _run_validation(self, value):
        if self.options['required'] is True and value is _null:
            raise ValidationError(self.name, 'Required field not set')
        if self.options['required'] is False and (value is None or value is _null):
            raise SkipError
        self.default_validator(value)
        for validator in self.options['validators']:
            validator(self.name, value)

    def default_validator(self, value):
        """The default validator for a `Field` type which will always be applied.

        Note: This is only applied after all the user supplied custom validators have been applied.

        Args:
            value (object): The provided value.

        Raises:
            ValidationError: Raised when validation failed.
        """
        pass


class BoolField(Field):
    """`Field` which takes a boolean type.
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, bool):
            raise ValidationError(self.name, 'Not of bool type')


class CharField(Field):
    """`Field` which takes a character type which is a string of maximum length 1.
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.name, 'Not of str type')
        length = len(value)
        if length == 0 or length > 1:
            raise ValidationError(self.name, 'Should have length: 1 but has length: %s' % length)


class StrField(Field):
    """`Field` which takes a `str` type.
    """
    def __init__(self, min_length=None, max_length=None, **options):
        """
        Args:
            min_length (int, optional): The minimum length of string. Defaults to unbounded.
            max_length ([type], optional): The maximum length of string. Defaults to unbounded.
        """
        super().__init__(min_length=min_length, max_length=max_length, **options)

    def default_validator(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.name, 'Not of str type')
        validator = validators.length(min_length=self.options.get('min_length'),
                                      max_length=self.options.get('max_length'))
        validator(self.name, value)


class NumericField(Field):
    """`Field` which takes a `numeric` type.
    """
    def __init__(self, min_value=None, max_value=None, **options):
        """
        Args:
            min_value (int, optional): If given, the provided value should be greater than this.
            max_value (int], optional): If given, the provided value should be less than this.
        """
        super().__init__(min_value=min_value, max_value=max_value, **options)

    def default_validator(self, value):
        if not isinstance(value, numbers.Number):
            raise ValidationError(self.name, 'Not of numeric type')
        validator = validators.interval(min_value=self.options.get('min_value'),
                                        max_value=self.options.get('max_value'))
        validator(self.name, value)


class IntField(NumericField):
    """`Field` which takes an `int` type.
    """
    def default_validator(self, value):
        super().default_validator(value)
        if not isinstance(value, int):
            raise ValidationError(self.name, 'Not of int type')


class FloatField(NumericField):
    """`Field` which takes a `float` type.
    """
    def default_validator(self, value):
        super().default_validator(value)
        if not isinstance(value, float):
            raise ValidationError(self.name, 'Not of float type')


class DateField(Field):
    """`Field` which takes a `date` type
    """
    def default_validator(self, value):
        if isinstance(value, datetime) or not isinstance(value, date):
            raise ValidationError(self.name, 'Not of date type')


class DateTimeField(Field):
    """`Field` which takes a `datetime` type.
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, datetime):
            raise ValidationError(self.name, 'Not of datetime type')


class EmailField(Field):
    """`Field` which takes an email `str`.
    What constitutes an email is very lax and it only checks for presence of '@' and domain.
    There is no fool-proof way to confirm a valid email unless an email is sent at that address.
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.name, 'Not of str type')
        error = False
        try:
            if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', value):
                error = True
        except TypeError:
            error = True
        if error:
            raise ValidationError(self.name, 'Not a valid email')


class DictField(Field):
    """`Field` which takes a `dict` type.
    """
    def default_validator(self, value):
        if not isinstance(value, dict):
            raise ValidationError(self.name, 'Not of dict type')


class FireDataField(Field):
    """`Field` which takes a `FireData` type.

    Example:
        ```python
            class Foo(FireData):
                a = IntField()

            field = ListField(FireDataField(Foo))
            # 'field' can now contain a list of 'Foo' instances.
        ```
    """
    def __init__(self, data_class, **options):
        super().__init__(**options)
        self.data_class = data_class

    def default_validator(self, value):
        if not isinstance(value, self.data_class):
            raise ValidationError(self.name, 'Not of %s type' % self.data_class)
        value.validate()


class ListField(Field):
    """`Field` which takes a collection of other Fields.
    """
    def __init__(self, item, min_length=None, max_length=None, **options):
        """It allows theoretically infinite number of nested fields. For example:

            ListField(ListField(ListField(CharField())))
            
            for an input value:

            [[['a', 'b'], ['c', 'd']], [['e'], ['f', 'g']]]

        Valid input values should either be of `list` or `tuple` type.

        Args:
            item (Field): An instance of a `Field` type which this `list` will hold.
            min_length (int, optional): If given, the length of the provided `list` should be greater than this.
            max_length (int, optional): If given, the length of the provided `list` should be less than this.
        """

        assert isinstance(item, Field), 'ListField needs a Field type as nested item type'
        super().__init__(min_length=min_length, max_length=max_length, **options)
        self.item = item

    def _run_validation(self, value):
        super()._run_validation(value)
        for i, v in enumerate(value):
            try:
                self.item.__set_name__(self, '[%s]' % i)
                self.item._run_validation(v)
            except ValidationError as ex:
                field = self.name + ex.field
                raise ValidationError(field, ex.msg)
            except SkipError:
                pass

    def default_validator(self, value):
        valid_type = isinstance(value, list) or isinstance(value, tuple)
        if not valid_type:
            raise ValidationError(self.name, 'Not of list or tuple type')
        validator = validators.length(min_length=self.options.get('min_length'), max_length=self.options.get('max_length'))
        validator(self.name, value)
