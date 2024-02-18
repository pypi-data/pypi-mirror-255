# PetDB

PetDB is a simple and lightweight NOSQL JSON database for pet projects.
It was designed with the convenient and comfortable mongo-like API.
In this package also was implemented simple array with the same API,
that supports not only dict documents but any built-in python type.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/petdb)
![PyPI - Version](https://img.shields.io/pypi/v/petdb)
![Documentation Status](https://readthedocs.org/projects/petdb/badge/?version=latest)
![PyPI - License](https://img.shields.io/pypi/l/petdb)

## Installation

PetDB can be installed with [pip](http://pypi.python.org/pypi/pip):

```bash
python -m pip install petdb
```

You can also download the project source and do:

```bash
pip install .
```

## Dependencies

PetDB was created as a lightweight package, so there are no dependencies.

## Usage

To use this database you should only import PetDB and create an instance.
By default, it will create folder for storing collections in the current directory,
but you can provide any path:

```python
from petdb import PetDB

db = PetDB(os.path.join(os.getcwd(), "persistent", "storage"))
```

Next you should select the collection, if it doesn't exist, it will created automatically.
You can do it just by attribute access, by index key or use a method (it will create a new one if it doesn't exist):

```python
users = db.users
subscriptions = db["subscriptions"]
payments = db.collection("payments")
```

## Examples

```pycon
>>> from petdb import PetDB
>>> db = PetDB()
>>> users = db["users"]
>>> users.insert_many([
...     {"name": "John", "age": 28, "subscriptions": ["tv", "cloud"]},
...     {"name": "Michael", "age": 32, "subscriptions": ["tv"]},
...     {"name": "Sam", "age": 18, "subscriptions": ["music", "cloud"]},
...     {"name": "Alex", "age": 24, "subscriptions": ["tv", "music"]},
...     {"name": "Bob", "age": 18, "subscriptions": ["music"]},
... ])
[{"name": "John", "age": 28, "subscriptions": ["tv", "cloud"], "_id": "..."}, ...]
>>> users.update(
...     {"$append": {"subscriptions": "games"}},
...     {"age": {"$lt": 25}, "subscriptions": {"$contains": "music"}}
... )
>>> selection = users.filter({"age": 18}).sort("name")
>>> print(selection.flat("name").list())
["Bob", "Sam"]
>>> selection.remove()
[{"name": "Bob", "age": 18, "subscriptions": ["music", "games"], "_id": "..."},
{"name": "Sam", "age": 18, "subscriptions": ["music", "cloud", "games"], "_id": "..."}]
>>> for user in users:
...     print(user)
...
{'name': 'John', 'age': 28, 'subscriptions': ['tv', 'cloud'], '_id': '...'}
{'name': 'Michael', 'age': 32, 'subscriptions': ['tv'], '_id': '...'}
{'name': 'Alex', 'age': 24, 'subscriptions': ['tv', 'music', 'games'], '_id': '...'}
```

### Documentation

Documentation is available at https://petdb.readthedocs.io/en/latest/

## Testing

```bash
python -m tests
```
