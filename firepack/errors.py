class FirePackError(Exception):
    """Base class for `FirePack` errors.
    """


class SkipError(FirePackError):
    """Raising this error skips further execution.
    """


class ValidationError(FirePackError):
    """This exception contains input validation errors.
    """
    def __init__(self, field, msg, prefix='Field'):
        """
        Args:
            field (str): The name of the field.
            msg (str): The error description.
        """
        super().__init__('%s "%s": %s' % (prefix, field, msg))
        self.field = field
        self.msg = msg


class MultiValidationError(FirePackError):
    """This exception contains list of ValidationError exception instances.
    """
    def __init__(self, errors):
        self.errors = errors
        """The `errors` attribute is a list of `ValidationError` which contains `field` and `msg`attributes describing the field name and error description.
        """


class ParamError(FirePackError):
    """This error is raised when input contains a key which doesn't match any declared fields.
    """
    def __init__(self, field, msg='Not declared in class'):
        super().__init__('%s: %s' % (field, msg))
        self.field = field
        self.msg = msg


class DataError:
    pass
