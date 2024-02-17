import datetime
from itertools import (
    chain,
    islice,
)
from typing import (
    Iterable,
    Union,
)


def now():
    """Текущее время в UTC."""
    return datetime.datetime.now(datetime.timezone.utc)


def as_text(v: Union[bytes, str]) -> str:
    """Конвертирует последовательность байт в строку."""
    if isinstance(v, bytes):
        return v.decode('utf-8')
    elif isinstance(v, str):
        return v
    else:
        raise ValueError('Неизвестный тип %r' % type(v))


def make_chunks(
    iterable: Iterable,
    size: int,
    is_list: bool = False,
):
    """Нарезка итерабельного объекта на куски."""
    iterator = iter(iterable)

    for first in iterator:
        yield (
            list(chain([first], islice(iterator, size - 1)))
            if is_list
            else chain([first], islice(iterator, size - 1))
        )
