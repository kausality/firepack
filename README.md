# FirePack

FirePack is a minimalist Python library for creating services, data serialization and validation.

* Declarative input fields with validation.
* Service classes.
* Works with native Python objects wherever possible.
* Extensible with custom field types and validators.
* Data objects support serialization and validation along with nested references for complex datatypes.

## Installation

To install FirePack using pip, run: ```pip install git+https://github.com/kpchand/firepack.git```


# Basic Usage

## Creating services

```python
from firepack.fields import IntField, StrField
from firepack.service import FireService
from firepack.errors import SkipError, ValidationError


CRAWLED_DB = []

def page_name_validator(name, value):
    if not value.endswith('.html'):
        raise ValidationError(name, 'I only know html pages!')


class Crawler(FireService):
    # All fields are required by default
    user_id = IntField(min_value=1)
    # We use our own custom validator for page name
    page_name = StrField(validators=[page_name_validator])  

    def url(self):
        # Fields are directly accessible using instance __dict__
        return 'http://example.com/{}/{}'.format(self.user_id, self.page_name)

    def pre_fire(self):
        # This is called before fire. Useful for validation/instantiation
        if self.url() in CRAWLED_DB:
            # Control directly goes to post_fire method
            raise SkipError('Page already crawled!')
    
    def fire(self, **kwargs):
        # This is the entrypoint of service.
        CRAWLED_DB.append(self.url())

    def post_fire(self, fired, exc):
        # Called after execution of fire. Useful for cleanup operations.
        if fired:
            print('I crawled!')
        else:
            print('I skipped crawling because: ', exc)


crawler = Crawler()
# call() performs fields validation and if everything is in order, it calls fire() method
crawler.call({
    'user_id': 1,
    'page_name': 'about.html'
})

# Values are stored in native python types wherever possible:
print(type(crawler.user_id), type(crawler.page_name))  # <class 'int'> <class 'str'>
```

A slightly convoluted example to show nested field types:

```python
from firepack.service import FireService
from firepack.fields import ListField, CharField


class Service(FireService):
    a = ListField(ListField(ListField(CharField())))

    def fire(self, **kwargs):
        print(self.a)


s = Service()
s.call({
    'a': [[['a', 'b'], ['c', 'd']], [['e', 'f'], ['g', 'h']]]
})

```


## Object Serialization

`FireData` supports object serialization and converting complex datatypes to and from python native datatypes.
You can use nested references to create complex relationships between data objects. `FireData` instances can be used to pass around complex data structures from or to other services.

Example:
```python
from firepack.fields import IntField
from firepack.data import FireData


class FooData(FireData):
    a = IntField(required=True, min_value=1)


class BarData(FireData):
    a = IntField()
    b = FooData()  # nested reference to data object


# Let us assign some values
foo = FooData()
foo. a = 1

bar = BarData()
bar.a = 2
bar.b = foo

# Serialization: Converting FireData to json string
json_string = bar.to_json()
print(json_string)  # {"a": 2, "b": {"a": 1}}

# Deserialization: Loading json string into FireData
bar = BarData.load(json_string)
assert bar.a == 2
assert bar.b.a == 1

# Oh and you can also directly convert FireData instance to python dict
print(bar.to_dict())  # {'a': 2, 'b': {'a': 1}}
```


## Custom Fields

We can also create custom fields. Suppose our application takes user ID with the pattern *xxx-yyy-zzz*. We can create a `StringField ` and use a custom *validator*. But it would be more convenient & declarative if we had a `Field` type which did this validation by default. Here is an example of such an implementation:

Example:

```python
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

```


## Documentation

View the Docs [here](https://kpchand.github.io/firepack/firepack/index.html).


## What is a Service?

Services are a part of the domain model which performs some business logic. Usually they work on a set of inputs and change some state or return a computed value. In languages like Python which are not type safe, input validation and a common interface for programs which work on dynamic inputs could be an issue.

Some reading resources :
* https://en.wikipedia.org/wiki/Service_layer_pattern
* https://www.martinfowler.com/bliki/AnemicDomainModel.html


## Contributing

To generate docs use:
```angular2html 
pdoc3 --html -f -c sort_identifiers=False --output-dir docs firepack
```