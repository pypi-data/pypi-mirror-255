import logging
import os
import signal
import time
from enum import (
    Enum,
)
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Tuple,
    Union,
)
from uuid import (
    uuid4,
)

from firebase_admin.exceptions import (
    PERMISSION_DENIED,
)
from redis.exceptions import (
    ConnectionError,
)

from fcm_notifier import (
    VERSION,
    settings,
)
from fcm_notifier.helpers import (
    setup_log_handlers,
)


logger = logging.getLogger('fcm_notifier.worker')

if TYPE_CHECKING:
    from fcm_notifier.notification import (
        Notification,
    )
    from fcm_notifier.queue import (
        Queue,
    )
    from fcm_notifier.results import (
        BatchResult,
    )
    from fcm_notifier.sender import (
        FCMSender,
    )


class WorkerStatus(str, Enum):
    """Статус воркера."""

    BUSY = 'busy'  # В процессе работы
    IDLE = 'idle'  # Ожидает


class Worker:
    """Воркер."""

    worker_namespace_prefix = 'fcm_notifier:worker:'
    # коэффициент увеличения времени ожидания подключения в случае потери соединения к Redis
    exponential_backoff_factor = 2.0
    # максимальное время ожидания (в секундах) для повторной попытки при потере соединения с Redis
    max_connection_wait_time = 60.0

    def __init__(
        self,
        queue: 'Queue',
        sender: 'FCMSender',
        name: Optional[str] = None,
        logging_level: Union[str, int] = logging.INFO,
    ):
        self.queue = queue
        self.sender = sender
        self.name: str = name or uuid4().hex
        self.log = logger
        self._state = WorkerStatus.IDLE
        setup_log_handlers(logging_level, name=logger.name)

    @property
    def key(self):
        return self.worker_namespace_prefix + self.name

    def set_state(self, state: WorkerStatus) -> None:
        """Установка состояния воркера."""
        self._state = state
        # TODO: хранить состояние в redis?

    def request_stop(self, signum, frame):
        """Обработчик сигналов завершения работы воркера."""
        self.log.info(f'Worker {self.key}: остановка...')
        # TODO: корректное завершение работы
        raise SystemExit()

    def _install_signal_handlers(self):
        """Установка обработчиков сигналов системы для корректного завершения воркера."""
        signal.signal(signal.SIGINT, self.request_stop)
        signal.signal(signal.SIGTERM, self.request_stop)

    def dequeue(self, batch_size: Optional[int] = None) -> List['Notification']:
        """Получение из очереди сообщений."""
        connection_wait_time = 1.0

        while True:
            try:
                if batch_size is None or batch_size == 1:
                    return [self.queue.dequeue_notification(self.name)]
                elif batch_size > 1:
                    return self.queue.dequeue_notifications(count=batch_size, consumer_id=self.name)
                else:
                    return []

            except ConnectionError as err:
                self.log.error(f'Не удалось установить соединение с Redis: {err}')
                self.log.error(f'Повторная попытка через {connection_wait_time} секунды...')

                time.sleep(connection_wait_time)
                connection_wait_time *= self.exponential_backoff_factor
                connection_wait_time = min(connection_wait_time, self.max_connection_wait_time)

    def clean_processing_queue(self, results: 'BatchResult') -> Tuple[bool, int]:
        """Очистка processing очереди.

        Уведомления с ошибкой отправки возвращаются в основную очередь для повторной отправки.
        Если уведомление не было отправлено из-за ошибки доступа, то оно переотправляться не будет.
        """
        pushed_count = self.queue.push_to_queue(
            [res.id for res in results.failed if res.exc_code != PERMISSION_DENIED],
            settings.NOTIFICATION_TTL_REDUCE_FACTOR,
        )
        cleaned = self.queue.clean_processing_queue(self.name)

        return cleaned, pushed_count

    def save_results(self, results: 'BatchResult'):
        """Сохранение результатов отправки."""
        for result in results:
            self.queue.save_result(result)

    def work(
        self,
        batch_size: Optional[int] = None,
        idle_timeout: int = settings.WORKER_IDLE_TIMEOUT,
    ) -> None:
        """Основной метод работы."""
        if not self.sender.project_id:
            self.log.error('Не найдены учётные данные для FCM!')
            raise SystemExit()
        else:
            self.log.info(f'Firebase project ID: {self.sender.project_id}')

        self.log.info(self.queue.connection_info)
        self.log.info('Worker %s запущен с PID %d, версия %s', self.key, os.getpid(), VERSION)
        self.log.info(f'Используется очередь: {self.queue}')
        self.log.info(f'Количество сообщений в очереди: {len(self.queue)}')

        self._install_signal_handlers()

        self.log.debug('Обслуживание processing очереди...')
        returned, removed = self.queue.maintain_processing_queue(self.name)
        self.log.debug(f'{returned} возвращено в основную очередь, {removed} удалено из очереди.')

        while True:
            try:
                self.log.debug(f'Получение сообщений из очереди {self.queue}...')
                notifications = self.dequeue(batch_size)
                self.log.info(f'Получено {len(notifications)} сообщений из очереди {self.queue}')

                if notifications:
                    self.log.debug(f'Отправка {len(notifications)} уведомлений...')
                    results = self.sender.send_all(notifications)
                    self.log.info(
                        f'Отправлено: успешно - {len(results.successful)}; '
                        f'неудачно - {len(results.failed)}; '
                        f'недействующие токены - {len(results.invalid_token)}'
                    )
                    self.log.debug(
                        f'id уведомления | токен | результат отправки:\n\t%s',
                        '\n\t'.join(
                            f'{res.id} | {res.token} | {"OK" if not res.exc_string else res.exc_string}'
                            for res in results
                        )
                    )

                    cleaned, pushed_count = self.clean_processing_queue(results)

                    if len(results.failed):
                        self.log.info(f'Возвращено {pushed_count} уведомлений из processing в основную очередь.')

                    if cleaned:
                        self.log.debug('Очередь processing очищена.')
                    else:
                        self.log.error('Ошибка очистки processing очереди!')

                    self.save_results(results)

                if len(self.queue) >= batch_size:
                    # Если в очереди скопилось больше сообщений, чем отправляем за раз, то
                    # ожидать не будем, чтобы очередь не переполнялась и воркер её успевал обрабатывать
                    continue

                # Таймаут ожидания перед получением следующей пачки уведомлений из очереди
                time.sleep(idle_timeout)

            except SystemExit:
                # Cold shutdown detected
                raise

            except:  # noqa E722
                self.log.error('Worker %s: found an unhandled exception, quitting...', self.key, exc_info=True)
                break
