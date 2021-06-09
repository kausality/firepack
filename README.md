# FirePack

FirePack is a minimalist Python library for creating services, data serialization and validation.

* Declarative input fields with validation and immutability.
* Service classes.
* Works with native Python objects wherever possible.
* Extensible with custom field types and validators.
* Data objects support serialization and validation along with nested references for complex datatypes.

## Installation

To install FirePack using pip, run: ```pip install firepack```

To install FirePack using pipenv, run: ```pipenv install firepack```


## Basic Usage

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
    page_name = StrField(validators=[page_name_validator])

    def url(self):
        # Fields are directly accessible using instance __dict__
        return 'http://example.com/{}/{}'.format(self.user_id, self.page_name)

    def pre_fire(self):
        if self.url() in CRAWLED_DB:
            # Control directly goes to post_fire method
            raise SkipError('Page already crawled!')
    
    def fire(self, **kwargs):
        CRAWLED_DB.append(self.url())

    def post_fire(self, fired, exc):
        if fired:
            print('I crawled!')
        else:
            print('I skipped crawling because: ', exc)


crawler = Crawler()
crawler.call({
    'user_id': 1,
    'page_name': 'about.html'
})

# Values are stored in native python types wherever possible:
print(type(crawler.user_id), type(crawler.page_name))  # <class 'int'> <class 'str'>

# Raises ModificationError as all Fields are immutable
crawler.user_id = 2 
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


f = FooData()
f. a = 1

b = BarData()
b.a = 2
b.b = f

ret = b.to_dict()
print(ret)  # {'a': 2, 'b': {'a': 1}}
```


## Custom Fields

We can also create custom fields. Suppose our application takes user ID with the pattern *xxx-yyy-zzz*. We can create a `StringField ` and use a custom *validator*. But it would be more convenient & declarative if we had a `Field` type which did this validation by default. Here is an example of such an implementation:

Example:

```python
from firepack.fields import StrField
from firepack.errors import ValidationError
from firepack.service import FireService


class IDField(StrField):
    """A Field which takes input in the pattern xxx-yyy-zzz.
    """
    def default_validator(self, value):
        # Use StringField validator to validate str
        super().default_validator(value)
        value = value.split('-')
        if len(value) != 3 or not all([len(v) == 3 for v in value]):
            raise ValidationError(self.name, 'Improper format')


class Service(FireService):
    user_id = IDField()

    def fire(self, **kwargs):
        print('user_id: ', self.user_id)


s = Service()
s.call({
    'user_id': 'foo-bar-baz'
    }
)
```


## Documentation

View the Docs at: https://kpchand.github.io/firepack/firepack.
If the page fails to load, then directly go [here](https://kpchand.github.io/firepack/firepack/index.html).


## What is a Service?

Services are a part of the domain model which performs some business logic. Usually they work on a set of inputs and change some state or return a computed value. In languages like Python which are not type safe, input validation and a common interface for programs which work on dynamic inputs could be an issue.

Some reading resources :
* https://en.wikipedia.org/wiki/Service_layer_pattern
* https://www.martinfowler.com/bliki/AnemicDomainModel.html
