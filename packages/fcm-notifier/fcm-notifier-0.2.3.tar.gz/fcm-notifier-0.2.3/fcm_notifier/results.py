import datetime
from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
)
from typing import (
    Iterator,
    List,
    Optional,
)

from fcm_notifier.utils import (
    now,
)


class ResultStatus(Enum):
    """Статус результата отправки."""

    SUCCESSFUL = 1
    FAILED = 2
    INVALID_TOKEN = 3


@dataclass
class Result:
    """Результат отправки."""

    id: str
    token: str
    status: ResultStatus

    fcm_message_id: str = ''
    exc_code: str = ''
    exc_string: str = ''
    created_at: 'datetime.datetime' = now()


class BatchResult:
    """Перечень результатов отправки."""

    def __init__(self, results: List['Result']) -> None:
        self._results = results
        self._successful_results = None
        self._failed_results = None
        self._invalid_token_results = None

    def __len__(self):
        return len(self._results)

    def __getitem__(self, i: int) -> Optional['Result']:
        return self._results[i]

    def __contains__(self, item: Result) -> bool:
        return item in self._results

    def __iter__(self) -> Iterator['Result']:
        return iter(self._results)

    def __reversed__(self) -> Iterator['Result']:
        return reversed(self._results)

    @property
    def results(self) -> List['Result']:
        """Возвращает перечень результатов."""
        return self._results

    @property
    def successful(self) -> List['Result']:
        """Возвращает результаты по успешно отправленным сообщениям."""
        if self._successful_results is None:
            self._successful_results = [
                res for res in self._results if res.status == ResultStatus.SUCCESSFUL
            ]
        return self._successful_results

    @property
    def failed(self) -> List['Result']:
        """Возвращает результаты по неотправленным сообщениям из-за ошибок."""
        if self._failed_results is None:
            self._failed_results = [
                res for res in self._results if res.status == ResultStatus.FAILED
            ]
        return self._failed_results

    @property
    def invalid_token(self) -> List['Result']:
        """Возвращает результаты по неотправленным сообщениям из-за недействующего токена."""
        if self._invalid_token_results is None:
            self._invalid_token_results = [
                res for res in self._results if res.status == ResultStatus.INVALID_TOKEN
            ]
        return self._invalid_token_results
