import os
from typing import Iterator

from petdb.pcollection import PetCollection

class PetDB:
	"""
	The main class of PetDB.

	The ``PetDB`` class is responsible for storing and managing this database's collections.

	Collections access is provided by forwarding all unknown method calls
	and property access operations to the :py:meth:`PetDB.collection` method
	by implementing :py:meth:`PetDB.__getattr__` and :py:meth:`PetDB.__getitem__`.

	:param root: The root path where the folder for storing will be created
	"""

	def __init__(self, root: str = None):
		if root is None:
			root = os.getcwd()
		if not os.path.exists(root):
			raise Exception("Root directory does not exist")
		self.__root = os.path.join(root, "petstorage")
		if not os.path.exists(self.__root):
			os.mkdir(self.__root)
		self.__collections: dict[str, PetCollection] = {}
		self.__load_collections()

	def collection(self, name: str) -> PetCollection:
		"""
		Get access to the specific collection with the given name.

		If the collection hasn't been accessed yet, a new collection instance will be
		created. Otherwise, the previously created collection instance will be returned.

		:param name: The name of the collection.
		:return: :py:class:`PetCollection`
		"""
		if name not in self.__collections:
			return self.__create_collection(name)
		return self.__collections[name]

	def collections(self) -> list[str]:
		"""
		Get the names of all collections in the database.

		:returns: a list of collections names
		"""
		return list(self.__collections.keys())

	def drop_collection(self, name: str):
		"""
		Deletes the collection with the given name

		:param name: The name of the collection to delete
		"""
		if name in self.__collections:
			self.__collections[name].clear()
			self.__collections.pop(name)
			os.remove(os.path.join(self.__root, f"{name}.json"))

	def drop(self) -> None:
		"""
		Drop all collections from the database. **CANNOT BE REVERSED!**
		"""
		for name in self.__collections:
			self.drop_collection(name)

	def __getattr__(self, name: str) -> PetCollection:
		"""
		Alias for :py:meth:`PetDB.collection`

		:return: :py:class:`PetCollection`
		"""
		return self.collection(name)

	def __getitem__(self, name: str) -> PetCollection:
		"""
		Alias for :py:meth:`PetDB.collection`

		:return: :py:class:`PetCollection`
		"""
		if not isinstance(name, str):
			raise TypeError("Name must be a string")
		return self.collection(name)

	def __load_collections(self):
		for file in os.listdir(self.__root):
			if not file.endswith(".json"):
				continue
			self.__collections[file.rsplit(".", 1)[0]] = PetCollection(os.path.join(self.__root, file))

	def __create_collection(self, name: str):
		self.__collections[name] = PetCollection(os.path.join(self.__root, f"{name}.json"))
		return self.__collections[name]

	def __len__(self):
		return len(self.__collections)

	def __iter__(self) -> Iterator[PetCollection]:
		return iter(self.__collections.values())
