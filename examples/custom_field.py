from firepack.fields import StrField
from firepack.errors import ValidationError, MultiValidationError
from firepack.service import FireService


class IDField(StrField):
    """A Field which takes input in the pattern xxx-yyy-zzz.
    """
    def default_validator(self, value):
        # Use StrField default validator to validate initial string
        super().default_validator(value)
        value = value.split('-')
        if len(value) != 3 or not all([len(v) == 3 for v in value]):
            raise ValidationError(self.name, 'Improper format')


class Service(FireService):
    user_id = IDField()

    def fire(self, **kwargs):
        print('user_id: ', self.user_id)


s = Service()

try:
    s.call({
    'user_id': 'foo-bar'  # will throw exception, should be in form foo-bar-baz
        }
    )
except MultiValidationError as ex:
    for error in ex.errors:
        print('%s: has error: %s' % (error.field, error.msg))
