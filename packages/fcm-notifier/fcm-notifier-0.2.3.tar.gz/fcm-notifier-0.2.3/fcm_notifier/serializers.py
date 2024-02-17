import json
import pickle
from abc import (
    ABC,
    abstractmethod,
)
from functools import (
    partial,
)


class Serializer(ABC):
    """Абстрактный сериализатор."""

    @classmethod
    @abstractmethod
    def dumps(cls, obj: object) -> bytes:
        """Сериализация данных."""

    @classmethod
    @abstractmethod
    def loads(cls, s: bytes) -> object:
        """Десериализация данных."""


class PickleSerializer(Serializer):
    """Сериализатор объектов Python."""

    dumps = partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL)
    loads = pickle.loads


class JSONSerializer(Serializer):
    """Сериализатор JSON."""

    @staticmethod
    def dumps(*args, **kwargs):
        return json.dumps(*args, **kwargs).encode('utf-8')

    @staticmethod
    def loads(s, *args, **kwargs):
        return json.loads(s.decode('utf-8'), *args, **kwargs)
