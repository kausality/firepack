import json
from firepack.fields import Field, DictField
from firepack.errors import FirePackError, SkipError, ValidationError, MultiValidationError, ParamError


class FireData:
    """Class which provides support for object serialization and converting complex datatypes to and from python native datatypes.
    This can be visualized as a structure with support for nesting and validation.

    Example:

    ```python
    class FooData(FireData):
        a = IntField()


    class BarData(FireData):
        a = IntField()
        b = FooData()


    f = FooData()
    f. a = 1

    b = BarData()
    b.a = 2
    b.b = f

    ret = b.to_dict()
    print(ret)  # {'a': 2, 'b': {'a': 1}}
    ```
    """

    def __new__(cls, *args, **kwargs):
        # Initializes fields with default values
        # Otherwise field value if not set returns default values only if accessed
        # This setting of default values is not required in services because the call method takes care of it
        # by initializing fields which sets the field to provided value or the default if not provided
        instance = super(FireData, cls).__new__(cls)
        if kwargs.get('required'):
            instance.required = kwargs['required']
        attrs = instance._get_attrs()
        for name, obj in attrs:
            if isinstance(obj, Field):
                instance.__setattr__(name, obj.options['default'])
        return instance

    def __init__(self, required=True):
        self.required = required

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getattr__(self, name):
        self.__dict__.get(name)

    def to_json(self, **kwargs):
        """Converts `FireData` instance to a JSON string.

        Note: You can pass keyword arguments which maps to the arguments of python std lib method ```json.dumps()```.
        For ex: ```fire_data_instance.to_json(indent=4)```

        Returns:
            str: JSON string.
        """

        dct_data = self.to_dict()
        return json.dumps(dct_data, **kwargs)

    def to_dict(self):
        """Converts `FireData` instance to a `dict`.

        Returns:
            dict: Dictionary mapping each `Field` in the instance.
        """

        dct = dict()
        attrs = self._get_attrs()
        for name, obj in attrs:
            value = getattr(self, name)
            if isinstance(obj, FireData):
                value.validate()
                value = value.to_dict()
            dct[name] = value
        self.validate()
        return dct

    @classmethod
    def load(cls, data):
        """Takes a data value in either string or dict format and converts it into a `FireData` instance.

        Args:
            data: A data value. Can be of `str`(json), `dict` or `FireData` type.

        Returns:
            `FireData`: Initialized `FireData` instance.
        """
        if isinstance(data, dict):
            return cls.load_dict(data)
        if isinstance(data, str):
            return cls.load_json(data)
        if isinstance(data, FireData):
            return cls.load_dict(data.to_dict())
        raise FirePackError('Need a valid type which is either str, dict or of `FireData` type')

    @classmethod
    def load_json(cls, json_data, exact=True):
        """Takes a JSON string and converts it into a `FireData` instance with each declared `Field` attribute value mapping to corresponding JSON key's value.

        Args:
            json_data (str): JSON string.
            exact (bool, optional): If set to `True`, any key in `json_data` which doesn't maps to any declared `Field` attribute in the `FireData` class will raise `ParamError`. Defaults to True.

        Raises:
            ParamError: [description]

        Returns:
            `FireData`: Initialized `FireData` instance.
        """
        
        assert isinstance(json_data, str), 'JSON should be of type str'
        dct_data = json.loads(json_data)
        obj = cls._load_data_from_dict(dct_data, exact)
        return obj

    @classmethod
    def load_dict(cls, data_dict, exact=True):
        """Takes a `dict` and converts it into a `FireData` instance with each declare`Field` attribute value mapping to corresponding `dict` key's value.

        Args:
            data_dict (dict): Dictionary input.
            exact (bool, optional): If set to `True`, any key in `dct_data` which doesn't maps to any declared `Field` attribute in the `FireData` class will raise `ParamError`. Defaults to True.

        Returns:
            `FireData`: Initialized `FireData` instance.
        """

        obj = cls._load_data_from_dict(data_dict, exact)
        return obj

    @classmethod
    def _load_data_from_dict(cls, data, exact):
        assert isinstance(data, dict), 'Should be of dict type'

        attrs = cls._get_attrs()
        attrs_map = {i[0]: i[1] for i in attrs}  # dict: {attr_name: attr object(Field/FireData object)}
        attrs_names = [name for name, _ in attrs]
        obj = cls()
        for name, value in data.items():
            if exact and name not in attrs_names:
                raise ParamError(name)
            elif isinstance(value, dict) and isinstance(attrs_map[name], FireData):
                # load dict value as that mapping to a FireData class
                value = cls.__dict__[name].load(value)
            elif isinstance(value, dict) and isinstance(attrs_map[name], DictField):
                pass  # just keep value
            else:
                FirePackError('Cannot load attribute: %s with value: %s' % (name, value))
            setattr(obj, name, value)
            # should validate using field ??
        return obj

    @classmethod
    def _get_attrs(cls):
        def is_valid(obj):
            return isinstance(obj, Field) or isinstance(obj, FireData)
        attrs = []
        for klass in cls.__mro__:
            for name, obj in klass.__dict__.items():
                if is_valid(obj):
                    attrs.append((name, obj))
        return attrs

    def validate(self):
        """Validates all declared attributes in this `FireData` instance.

        Raises:
            MultiValidationError: Raised when `Field` values contains validation errors. 
        """

        attrs = self._get_attrs()
        errors = []
        for name, obj in attrs:
            value = self.__dict__.get(name)
            if isinstance(obj, FireData) and value is None:
                errors.append(ValidationError(name, 'FireData attribute not initialized'))
            elif isinstance(value, FireData):
                value.validate()
            else:  # field object
                try:
                    # obj is a descriptor so get the value which descriptor set in the instance class
                    # also return default value if none set
                    field_value = obj.__get__(self, type(self))
                    obj._run_validation(field_value)
                except ValidationError as ex:
                    errors.append(ex)
                except SkipError:
                    pass
        if errors:
            raise MultiValidationError(errors)

    def __str__(self):
        attrs = self._get_attrs()
        s = ''
        for name, obj in attrs:
            value = self.__dict__.get(name)
            s += '%s=%s' % (name, value) + ' | '
        return s

