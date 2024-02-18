import re
from typing import Any, Callable

from petdb.pexceptions import QueryException

class NonExistent:
	def __repr__(self):
		return "[Non-existent-object]"

NON_EXISTENT = NonExistent()

class PetUtils:

	OPERATORS = {
		"$eq": lambda q, v: v == q,
		"$ne": lambda q, v: v != q,
		"$lt": lambda q, v: v < q,
		"$<": lambda q, v: v < q,
		"$lte": lambda q, v: v <= q,
		"$<=": lambda q, v: v <= q,
		"$gt": lambda q, v: v > q,
		"$>": lambda q, v: v > q,
		"$gte": lambda q, v: v >= q,
		"$>=": lambda q, v: v >= q,
		"$in": lambda q, v: v in q,
		"$nin": lambda q, v: v not in q,
		"$notin": lambda q, v: v not in q,
		"$contains": lambda q, v: q in v,
		"$notcontains": lambda q, v: q not in v,
		"$length": lambda q, v: PetUtils.match(len(v), q),
		"$size": lambda q, v: PetUtils.match(len(v), q),
		"$exists": lambda q, v: q == (v != NON_EXISTENT),
		"$regex": lambda q, v: v and re.search(q, v),
		"$func": lambda q, v: q(v),
		"$where": lambda q, v: q(v),
		"$f": lambda q, v: q(v),
		"$type": lambda q, v: isinstance(v, q),
		"$is": lambda q, v: isinstance(v, q),
		"$and": lambda q, v: all(PetUtils.match(v, query) for query in q),
		"$all": lambda q, v: all(PetUtils.match(v, query) for query in q),
		"$or": lambda q, v: any(PetUtils.match(v, query) for query in q),
		"$any": lambda q, v: any(PetUtils.match(v, query) for query in q),
		"$not": lambda q, v: not PetUtils.match(v, q),
	}

	UPDATE_OPERATORS = {
		"$set": lambda q, doc: [PetUtils.set(doc, key, value) for key, value in q.items()],
		"$unset": lambda q, doc: [PetUtils.unset(doc, key) for key, value in q.items() if value],
		"$inc": lambda q, doc: [PetUtils.inc(doc, key, value) for key, value in q.items()],
		"$append": lambda q, doc: [PetUtils.append(doc, key, value) for key, value in q.items()],
		"$push": lambda q, doc: [PetUtils.append(doc, key, value) for key, value in q.items()],
		"$addToList": lambda q, doc: [PetUtils.append(doc, key, value) for key, value in q.items()],
		"$addToSet": lambda q, doc: [PetUtils.add_to_set(doc, key, value) for key, value in q.items()],
		"$map": lambda q, doc: [PetUtils.set(doc, key, func(PetUtils.get(doc, key))) for key, func in q.items()]
	}

	@classmethod
	def match[T](cls, obj: T, query: dict[str] | Callable[[Any], bool] | T) -> bool:
		if isinstance(query, Callable):
			return query(obj)
		elif not isinstance(query, dict):
			return obj == query

		for key in query:
			if key.startswith("$"):
				if not cls.OPERATORS[key](query[key], obj):
					return False
				continue

			value = cls.get(obj, key)
			if cls.is_operators_query(query[key]):
				for operator in query[key]:
					if not cls.OPERATORS[operator](query[key][operator], value):
						return False
			elif isinstance(value, dict) and isinstance(query[key], dict):
				if not cls.match(value, query[key]):
					return False
			elif value != query[key]:
				return False
		return True

	@classmethod
	def exists[T](cls, obj: T, query: dict[str] | Callable[[T], bool]) -> bool:
		if isinstance(query, Callable):
			return query(obj)
		elif not isinstance(query, dict):
			return obj == query

		for key in query:
			if key.startswith("$"):
				try:
					if not cls.OPERATORS[key](query[key], obj):
						return False
				except TypeError:
					return False
				continue

			value = cls.get(obj, key)
			if isinstance(value, NonExistent):
				return False
			elif cls.is_operators_query(query[key]):
				for operator in query[key]:
					try:
						if not cls.OPERATORS[operator](query[key][operator], value):
							return False
					except TypeError:
						return False
			elif isinstance(value, dict) and isinstance(query[key], dict):
				if not cls.exists(value, query[key]):
					return False
			elif value != query[key]:
				return False
		return True

	@classmethod
	def update(cls, obj: dict, update: dict):
		for operator in update:
			cls.UPDATE_OPERATORS[operator](update[operator], obj)

	@classmethod
	def is_operators_query(cls, query: Any) -> bool:
		if not isinstance(query, dict) or len(query) == 0:
			return False

		is_operators_query = list(query.keys())[0].startswith("$")
		for key in query:
			if is_operators_query != key.startswith("$"):
				raise QueryException("Invalid query: you can't combine operators query with the path objects")
		return is_operators_query

	@classmethod
	def get[T](cls, obj: T, key: str | int | Callable[[T], bool] = None, fill_path: bool = False):
		if key is None:
			if obj is None:
				return NON_EXISTENT
			return obj
		elif isinstance(key, Callable):
			try:
				return key(obj)
			except Exception:
				return NON_EXISTENT
		elif isinstance(key, int):
			if not isinstance(obj, list) or key >= len(obj):
				return NON_EXISTENT
			return obj[key]
		elif key == "&":
			return obj

		for field in key.split("."):
			if isinstance(obj, dict):
				if field not in obj:
					if not fill_path:
						return NON_EXISTENT
					obj[field] = {}
				obj = obj[field]
			elif isinstance(obj, list):
				if not field.isdigit() or int(field) >= len(obj):
					return NON_EXISTENT
				obj = obj[int(field)]
			else:
				return NON_EXISTENT
		return obj

	@classmethod
	def set(cls, obj: dict, key: str | int, value: Any):
		if isinstance(key, int):
			if not isinstance(obj, list):
				raise QueryException("Invalid append query: only lists supports integer keys")
			if key >= len(obj):
				raise QueryException("Invalid append query: index out of range")
			obj[key] = value
			return

		if "." in key:
			obj = cls.get(obj, key.rsplit(".", 1)[0], fill_path=True)
			if not isinstance(obj, (dict, list)):
				raise QueryException(f"Invalid set query: path {key} doesn't exist")
			key = key.rsplit(".", 1)[1]

		if isinstance(obj, dict):
			obj[key] = value
		elif isinstance(obj, list):
			if not key.isdigit():
				raise QueryException("Invalid set query: list index must contains only digits")
			if int(key) >= len(obj):
				raise QueryException("Invalid set query: list index out of range")
			obj[int(key)] = value
		else:
			raise QueryException(f"Invalid set query: path {key} doesn't exist")

	@classmethod
	def unset(cls, obj: dict, key: str) -> Any:
		if "." not in key:
			return obj.pop(key, None)

		obj = cls.get(obj, key.rsplit(".", 1)[0])
		if isinstance(obj, dict):
			return obj.pop(key.rsplit(".", 1)[1], None)

	@classmethod
	def inc(cls, obj: dict | list, key: str, value: Any):
		if "." in key:
			obj = cls.get(obj, key.rsplit(".", 1)[0], fill_path=True)
			if not isinstance(obj, (list, dict)):
				raise QueryException(f"Invalid inc query: path {key} doesn't exist")
			key = key.rsplit(".", 1)[1]

		if isinstance(obj, list):
			if not key.isdigit():
				raise QueryException("Invalid inc query: list index must contains only digits")
			if int(key) >= len(obj):
				raise QueryException("Invalid inc query: list index out of range")
			if not isinstance(obj[int(key)], int):
				raise QueryException("Invalid inc query: you can increment only integer values")
			obj[int(key)] += value
		elif isinstance(obj, dict):
			if key not in obj:
				obj[key] = 0
			if not isinstance(obj[key], int):
				raise QueryException(f"Invalid inc query: you can increment only integer values")
			obj[key] += value
		else:
			raise QueryException(f"Invalid set query: path {key} doesn't exist")

	@classmethod
	def append(cls, obj: dict, key: str | int, value: Any):
		if isinstance(key, int):
			if not isinstance(obj, list):
				raise QueryException("Invalid append query: only lists supports integer keys")
			if key >= len(obj):
				raise QueryException("Invalid append query: index out of range")
			if not isinstance(obj[key], list):
				raise QueryException("Invalid append query: it's impossible to append not to a list")
			obj[key].append(value)
			return

		obj = cls.get(obj, key)
		if obj == NON_EXISTENT:
			raise QueryException(f"Invalid append query: path {key} doesn't exist")
		elif not isinstance(obj, list):
			raise QueryException("Invalid append query: it's impossible to append not to a list")
		obj.append(value)

	@classmethod
	def add_to_set(cls, obj: dict, key: str | int, value: Any):
		if isinstance(key, int):
			if not isinstance(obj, list):
				raise QueryException("Invalid addToSet query: only lists supports integer keys")
			if key >= len(obj):
				raise QueryException("Invalid addToSet query: index out of range")
			if not isinstance(obj[key], list):
				raise QueryException("Invalid addToSet query: it's impossible to append not to a list")
			if value not in obj[key]:
				obj[key].append(value)
			return

		obj = cls.get(obj, key)
		if obj == NON_EXISTENT:
			raise QueryException(f"Invalid append query: path {key} doesn't exist")
		elif not isinstance(obj, list):
			raise QueryException("Invalid append query: it's impossible to append not to a list")
		if value not in obj:
			obj.append(value)

	@classmethod
	def remove(cls, data: list, query: dict | Callable[[Any], bool]):
		if not isinstance(query, dict):
			raise QueryException("Invalid delete query")
		deleted = []
		for item in data[:]:
			if cls.match(item, query):
				deleted.append(item)
				data.remove(item)
		return deleted
