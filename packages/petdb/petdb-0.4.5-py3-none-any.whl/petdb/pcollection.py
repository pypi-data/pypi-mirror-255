from __future__ import annotations

import os
import json
import uuid
from copy import deepcopy
from types import NoneType
from typing import Optional, Iterator, Self, Callable, Iterable, List, Any, Sized

from petdb.pexceptions import QueryException
from petdb.putils import PetUtils, NON_EXISTENT

type i_sort = str | int | Iterable[str | int] | Callable[[Any], Any] | None

class PetArray[T]:

	def __init__(self, data: List[T] = None):
		self._data: list[T] = data[:] if data is not None else []

	def find(self, query: dict | Callable[[T], bool]) -> Optional[T]:
		"""
		Returns the first element that satisfies the provided ``query``. If no values satisfy, ``None`` is returned.

		:param query: A query object that to match against
		:returns: The first matched element or ``None``
		"""
		for doc in self._data:
			if PetUtils.match(doc, query):
				return doc
		return None

	def findall(self, query: dict | Callable[[T], bool]) -> List[T]:
		"""
		Returns all elements that satisfy the provided ``query``. If no values satisfy, the empty list is returned.

		:param query: A query object that selects which documents to include in the result set
		:returns: List of matched documents
		"""
		return [doc for doc in self._data if PetUtils.match(doc, query)]

	def filter(self, query: dict | Callable[[T], bool]) -> PetArray:
		"""Perform filter mutation. Accepts only query object."""
		return PetArray(self.findall(query))

	def contains(self, query: T | dict | Callable[[T], bool]) -> bool:
		"""
		Check whether the collection contains a document matching a query.

		:param query: the query object
		"""
		for doc in self._data:
			if PetUtils.exists(doc, query):
				return True
		return False

	def exists(self, query: T | dict | Callable[[T], bool]) -> bool:
		"""Alias for :py:meth:`PetArray.contains`"""
		return self.contains(query)

	def sort(self, query: i_sort = None, reverse: bool = False) -> Self:
		"""Perform sort mutation. Accepts path, list of paths and sorting function."""
		if isinstance(query, (str, int, NoneType)):
			query = [query]

		def key(doc):
			res = []
			for field in query:
				value = PetUtils.get(doc, field)
				res.append((value == NON_EXISTENT, value))
			return res

		self._data.sort(key=query if isinstance(query, Callable) else key, reverse=reverse)
		return self

	def map[TP](self, func: Callable[[T], TP]) -> PetArray:
		"""Perform map mutation. Accepts only callable object."""
		return PetArray([func(doc) for doc in self._data])

	def flat(self, query: str | int | Callable[[T], bool]) -> PetArray:
		"""Perform flat mutation. Accepts only path."""
		return PetArray([value for doc in self._data if (value := PetUtils.get(doc, query)) != NON_EXISTENT])

	def foreach(self, func: Callable[[T], None]) -> None:
		"""
		Go through all elements and call the given function with each.

		:param func: function that takes each element in the array
		"""
		for element in self._data:
			func(element)

	def size(self) -> int:
		"""Returns the amount of all documents in the collection"""
		return len(self._data)

	def length(self) -> int:
		"""Returns the amount of all documents in the collection"""
		return self.size()

	def insert(self, element: T) -> T:
		"""
		Insert a new element into the array.

		:param element: the element to insert
		:returns: inserted element
		"""
		element = deepcopy(element)
		self._data.append(element)
		return element

	def insert_many(self, elements: Iterable[T]) -> list[T]:
		"""
		Insert multiple elements into the array.

		:param elements: an Iterable of elements to insert
		:returns: a list containing the inserted elements
		"""
		new_elements = [deepcopy(element) for element in elements]
		self._data.extend(new_elements)
		return new_elements

	def clear(self) -> List[T]:
		"""
		Removes all elements from the array.

		:return: Removed elements
		"""
		removed = self._data[:]
		self._data.clear()
		self._on_change()
		return removed

	def remove(self, query: dict) -> List[T]:
		"""
		Removes matched documents. Accepts id, query object, list of ids and list of documents.
		Performs clearing if the query is None. Returns removed documents.

		:returns: removed documents
		"""
		removed = PetUtils.remove(self._data, query)
		self._on_change()
		return removed

	def delete(self, query: dict) -> Self:
		"""Calls the remove method and returns self"""
		self.remove(query)
		return self

	def update(self, update: dict, query: dict | Callable[[T], bool] = None) -> Self:
		"""Applies update query to all elements that match the given query"""
		if not isinstance(update, dict):
			raise QueryException("Invalid update query: it should be a dict")
		if query is not None and not isinstance(query, (dict, Callable)):
			raise QueryException("Invalid query: it should be a dict or callable")
		for doc in self._data:
			if query is None or PetUtils.match(doc, query):
				PetUtils.update(doc, deepcopy(update))
		self._on_change()
		return self

	def update_one(self, update: dict, query: dict | Callable[[T], bool] = None) -> Self:
		"""Applies update query to a single element matching the given query"""
		item = self.find(query or {})
		if item is not None:
			PetUtils.update(item, deepcopy(update))
			self._on_change()
		return self

	def unique(self, query: str | int | Callable[[T], Any] = None):
		"""Removes all repeated elements"""
		keys = []
		result = []
		for element in self._data:
			key = PetUtils.get(element, query)
			if key not in keys:
				keys.append(key)
				result.append(element)
		return PetArray(result)

	def groupby(self, key: str | int | Iterable[str | int] | Callable[[T], Any] = None) -> PetArray:
		"""
		Groups elements by field accessed by a ``key``.

		:param key: The key or keys to access value or values to group elements by.
		:return: A PetArray of dicts with ``key`` and ``items`` fields.
		:raises QueryException: If the key type is not a string, integer or iterable of strings or integers.
		"""
		if isinstance(key, (str, int, NoneType)):
			get_key = lambda item: PetUtils.get(item, key)
		elif isinstance(key, Iterable):
			get_key = lambda item: tuple(PetUtils.get(item, k) for k in key)
		elif isinstance(key, Callable):
			get_key = lambda item: key(item)
		else:
			raise QueryException("Invalid group by key: it should be a string, integer, iterable, callable or None")
		result = {}
		for item in self._data:
			key_value = get_key(item)
			result.setdefault(key_value, []).append(item)
		return PetArray([{"key": key, "items": items} for key, items in result.items()])

	def join(self, delimiter: str, adapter: Callable[[T], str] = None) -> str:
		"""
		Compose all elements of a PetArray into the single string with the given ``delimiter``.

		:param delimiter: Separator used to join elements.
		:param adapter: Function to convert each element to string.
		:return: The concatenated string
		"""
		if adapter is None:
			adapter = lambda item: str(item)
		return delimiter.join(adapter(item) for item in self._data)

	def reduce[TP](self, reducer: Callable[[TP, T], TP], init: TP = None) -> TP:
		"""
		Executes the given "reducer" callback function on each element of the array,
		passing in the return value from the calculation on the preceding element.
		The final result of running the reducer across all elements of the array is a single value.

		:param reducer: A function to execute for each element in the array
			with the next signature: ``reducer(accumulator: TP, item: T) -> TP``.
			Its return value becomes the value of the ``accumulator`` parameter
			on the next invocation of reducer. For the last invocation,
			the return value becomes the return value of reduce(). The function is called
			with the following arguments:
		:param init: A value to which ``accumulator`` is initialized the first time the callback is called.
			If ``init`` is specified, ``reducer`` starts executing with the first value in the array as ``item``.
			If ``init`` is not specified, ``accumulator`` is initialized to the first value in the array, and
			``reducer`` starts executing with the second value in the array as currentValue. In this case,
			if the array is empty (so that there's no first value to return as ``accumulator``), a ``None`` is returned.
		:return: The value that results from running the ``reducer`` callback to completion over the entire array.
		"""
		result = init if init is not None else self._data[0] if self.size() > 0 else None
		for item in self._data[0 if init is not None else 1:]:
			result = reducer(result, item)
		return result

	def list(self) -> List[T]:
		"""
		Returns all documents stored in the collection as a list

		:returns: a list with all documents.
		"""
		return self._data[:]

	def _on_change(self):
		pass

	def __len__(self):
		return len(self._data)

	def __iter__(self) -> Iterator[T]:
		return iter(self._data)

	def __getitem__(self, item) -> T:
		return self._data[item]

	def __repr__(self):
		return f"<{self.__class__.__name__} size={self.size()}>"

class PetCollection(PetArray[dict]):
	"""
	Represents a single PetDB collection.
	It provides methods for accessing, managing and manipulating documents.

	:param path: Path to the json file where collection's documents are stored.
				It also used to specify the name of the collection.
	"""

	def __init__(self, path: str):
		self.__path = path
		self.name = os.path.basename(path).rsplit(".", 1)[0]
		if os.path.exists(self.__path):
			with open(self.__path, "r", encoding="utf-8") as f:
				super().__init__(json.load(f))
		else: super().__init__([])

	def dump(self) -> None:
		"""Dumps documents into a collection's storage file"""
		with open(self.__path, "w", encoding="utf-8") as f:
			json.dump(self._data, f, indent=4, ensure_ascii=False)

	def save(self) -> None:
		"""Alias for :py:meth:`PetCollection.dump`"""
		self.dump()

	def insert(self, doc: dict) -> dict:
		"""
		Insert a new document into the collection.

		:param doc: the document to insert
		:returns: inserted document
		"""
		if not isinstance(doc, dict):
			raise TypeError("Document must be of type dict")
		if "_id" in doc and self.get(doc["_id"]):
			raise QueryException("Duplicate id")
		doc = deepcopy(doc)
		if "_id" not in doc:
			doc["_id"] = str(uuid.uuid4())
		self._data.append(doc)
		self.dump()
		return doc

	def insert_many(self, docs: Iterable[dict] & Sized) -> list[dict]:
		"""
		Insert multiple documents into the collection.

		:param docs: an Iterable of documents to insert
		:returns: a list containing the inserted documents
		"""
		for doc in docs:
			if not isinstance(doc, dict):
				raise TypeError("Document must be of type dict")
			if "_id" in doc and self.get(doc["_id"]):
				raise QueryException("Duplicate id")
			doc = deepcopy(doc)
			if "_id" not in doc:
				doc["_id"] = str(uuid.uuid4())
			self._data.append(doc)
		self.dump()
		return self._data[-len(docs):]

	def update_one(self, update: dict, query: str | dict | list[str | dict] = None) -> None:
		if isinstance(query, str):
			query = {"_id": query}
		if isinstance(query, list):
			if all(isinstance(item, str) for item in query):
				query = {"_id": {"$in": query}}
			elif all(isinstance(item, dict) for item in query):
				query = {"_id": {"$in": [doc["_id"] for doc in query]}}
			else:
				raise QueryException("Invalid query format: query list should contains only ids or only docs")
		super().update_one(update, query)

	def update(self, update: dict, query: dict | list[str | dict] = None) -> None:
		if isinstance(query, list):
			if all(isinstance(item, str) for item in query):
				query = {"_id": {"$in": query}}
			elif all(isinstance(item, dict) for item in query):
				query = {"_id": {"$in": [doc["_id"] for doc in query]}}
			else:
				raise QueryException("Invalid query format: query list should contains only ids or only docs")
		if query is not None and not isinstance(query, dict):
			raise QueryException("Invalid query type: query should be dict or list")
		super().update(update, query)

	def remove(self, query: str | dict | list[str | dict]) -> list[dict]:
		if isinstance(query, str):
			query = {"_id": query}
		elif isinstance(query, list):
			if all(isinstance(item, str) for item in query):
				query = {"_id": {"$in": query}}
			elif all(isinstance(item, dict) for item in query):
				query = {"_id": {"$in": [doc["_id"] for doc in query]}}
			else:
				raise QueryException("Invalid delete query: it can only be a list of IDs or a list of docs")
		return super().remove(query)

	def get(self, id: str) -> Optional[dict]:
		"""
		Search for the document with the given ``id``.

		:param id: document's id to search
		:returns: the document with the given ``id`` or ``None``
		"""
		return self.find({"_id": id})

	def filter(self, query: dict | Callable[[dict], bool]) -> PetMutable:
		"""Perform filter mutation. Accepts only query object."""
		return PetMutable(self, self.findall(query))

	def sort(self, query: i_sort = None, reverse: bool = False) -> PetMutable:
		return PetMutable(self, self._data).sort(query)

	def _on_change(self):
		self.dump()

	def __repr__(self):
		return f"<{self.__class__.__name__} name={self.name} size={self.size()}>"

class PetMutable(PetArray[dict]):

	def __init__(self, col: PetCollection, data: list[dict]):
		super().__init__(data)
		self.__col = col

	def get(self, id: str) -> Optional[dict]:
		"""
		Search for a document with the given id

		:param id: document's id
		:return: a single document or ``None`` if no matching document is found
		"""
		return self.find({"_id": id})

	def filter(self, query: dict | Callable[[dict], bool]) -> PetMutable:
		"""Perform filter mutation. Accepts only query object."""
		return PetMutable(self.__col, self.findall(query))

	def insert(self, doc: dict) -> dict:
		"""
		Insert a new document into the parent collection.

		:param doc: the document to insert
		:returns: inserted document
		"""
		doc = self.__col.insert(doc)
		self._data.append(doc)
		return doc

	def insert_many(self, docs: Iterable[dict]) -> list[dict]:
		"""
		Insert multiple documents into the collection.

		:param docs: an Iterable of documents to insert
		:returns: a list containing the inserted documents
		"""
		docs = self.__col.insert_many(docs)
		self._data.extend(docs)
		return docs

	def update_one(self, update: dict, query: dict = None) -> None:
		"""Applies update query to a single element matching the given query"""
		super().update_one(update, query)
		self.__col.dump()

	def update(self, update: dict, query: dict = None) -> None:
		"""
		Applies update query to all documents in mutated list
		that matches the given query, affects the original collection
		"""
		super().update(update, query)
		self.__col.dump()

	def clear(self) -> List[dict]:
		"""
		Removes all documents from the current mutable array and removes all of them from the original collection.

		:return: Removed documents
		"""
		removed = self.__col.remove(self._data)
		self._data = []
		return removed

	def remove(self, query: dict) -> List[dict]:
		"""
		Removes matched documents, affects the original collection.
		Accepts id, query object, list of ids and list of documents.
		Performs clearing if the query is None. Returns removed documents.

		:returns: removed documents
		"""
		removed = super().remove(query)
		self.__col.remove(removed)
		return removed

	def __repr__(self):
		return f"<{self.__class__.__name__} name={self.__col.name} size={self.size()}>"
