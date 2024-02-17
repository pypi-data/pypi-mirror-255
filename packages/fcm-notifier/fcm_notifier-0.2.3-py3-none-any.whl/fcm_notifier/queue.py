import logging
from abc import (
    ABC,
    abstractmethod,
)
from functools import (
    partial,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from fcm_notifier import (
    settings,
)
from fcm_notifier.helpers import (
    get_redis_version,
    setup_log_handlers,
)
from fcm_notifier.results import (
    BatchResult,
    Result,
)
from fcm_notifier.serializers import (
    PickleSerializer,
    Serializer,
)
from fcm_notifier.utils import (
    as_text,
    make_chunks,
)


if TYPE_CHECKING:
    from redis import (
        Redis,
    )

    from fcm_notifier.notification import (
        Notification,
    )

logger = logging.getLogger('fcm_notifier.queue')


class Queue(ABC):
    """Абстрактная очередь."""

    queues_keys: str = 'fcm_notifier:queues'
    queue_processing_prefix: str = 'processing'
    queue_namespace_prefix: str = ''
    notification_prefix: str = ''
    result_prefix: str = ''

    def __init__(
        self,
        name: str = 'default',
        connection: Optional[Any] = None,
        serializer: Type['Serializer'] = PickleSerializer,
        logging_level: Union[str, int] = logging.INFO,
        **kwargs,
    ):
        """Инициализация объекта очереди Queue."""
        self.connection = connection
        self.name = name
        self._key = '{0}{1}'.format(self.queue_namespace_prefix, name)
        self.serializer = serializer
        self.log = logger
        setup_log_handlers(logging_level, name=logger.name)

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self.name)

    def __len__(self):
        return self.count

    def __bool__(self):
        return True

    @property
    def key(self):
        """Возвращает ключ этой очереди."""
        return self._key

    def get_processing_queue_key(self, consumer_id: str) -> str:
        """Возвращает ключ очереди потребителя."""
        return f'{self.key}{self.queue_processing_prefix}:{consumer_id}'

    @property
    @abstractmethod
    def count(self) -> int:
        """Возвращает кол-во всех сообщений в очереди."""

    def is_empty(self) -> bool:
        """Возвращает признак пустая ли очередь."""
        return self.count == 0

    @abstractmethod
    def empty(self) -> int:
        """Удаление всех уведомлений из очереди."""

    @classmethod
    def get_notification_key(cls, notification_id: str) -> str:
        """Возвращает ключ для уведомления."""
        return f'{cls.notification_prefix}{notification_id}'

    @classmethod
    def get_result_key(cls, result_id: str) -> str:
        """Возвращает ключ для результата."""
        return f'{cls.result_prefix}{result_id}'

    @abstractmethod
    def save_result(self, result: 'Result'):
        """Сохранение результата отправки."""

    @abstractmethod
    def get_result(self, result_id: str) -> Optional['Result']:
        """Получение сохраненного результата."""

    @abstractmethod
    def get_results(self, batch_size: int = settings.RESULT_BATCH_SIZE) -> Iterator['BatchResult']:
        """Получение всех результатов отправки."""

    @abstractmethod
    def enqueue_notification(self, notification: 'Notification') -> bool:
        """Добавление в очередь уведомления."""

    @abstractmethod
    def dequeue_notification(self, consumer_id: str) -> Optional['Notification']:
        """Возвращает из очереди уведомление."""

    @abstractmethod
    def dequeue_notifications(self, count: int, consumer_id: str) -> List['Notification']:
        """Возвращает из очереди перечень уведомлений."""

    @abstractmethod
    def maintain_processing_queue(self, consumer_id: str) -> Tuple[int, int]:
        """Обслуживание processing очереди."""

    @abstractmethod
    def push_to_queue(self, ids: List[str], ttl_reduce_factor: int = 0) -> int:
        """Возвращает указанные id уведомлений в очередь."""

    @abstractmethod
    def clean_processing_queue(self, consumer_id: str) -> bool:
        """Удаляет id уведомлений из processing очереди."""

    @property
    @abstractmethod
    def connection_info(self) -> str:
        """Информация об используемом соединении."""


class RedisQueue(Queue):
    """Очередь в Redis."""

    queue_namespace_prefix: str = 'fcm_notifier:queue:'
    notification_prefix = 'fcm_notifier:notification:'
    result_prefix = 'fcm_notifier:result:'

    def __init__(
        self,
        *args,
        connection: 'Redis',
        **kwargs,
    ):
        """Инициализация объекта очереди Queue."""
        super().__init__(*args, **kwargs)
        self.connection = connection
        self.redis_server_version = None

    @property
    def count(self) -> int:
        """Возвращает кол-во всех сообщений в очереди."""
        return self.connection.llen(self.key)

    def empty(self) -> int:
        """Удаление всех уведомлений из очереди.

        Возвращает кол-во удалённых элементов.
        Удаление производится с помощью Lua скрипта. Это обеспечивает
        как атомарность, так и выполняется быстрее.
        """
        script = """
            local prefix = "{0}"
            local q = KEYS[1]
            local count = 0
            while true do
                local n_id = redis.call("lpop", q)
                if n_id == false then
                    break
                end

                -- Delete the relevant keys
                redis.call("del", prefix..n_id)
                count = count + 1
            end
            return count
        """.format(self.notification_prefix).encode('utf-8')

        script = self.connection.register_script(script)

        return script(keys=[self.key])

    def save_result(self, result: 'Result'):
        """Сохранение результата отправки."""
        self.connection.set(self.get_result_key(result.id), self.serializer.dumps(result), ex=settings.RESULT_TTL)

    def get_result(self, result_id: str) -> Optional['Result']:
        """Получение сохраненного результата."""
        raw_result = self.connection.get(self.get_result_key(result_id))
        if raw_result:
            return self.serializer.loads(raw_result)

    def get_results(self, batch_size: int = settings.RESULT_BATCH_SIZE) -> Iterator['BatchResult']:
        """Получение всех результатов отправки."""
        result_keys = {
            as_text(result_key)
            for result_key in self.connection.scan_iter(match=f'{self.result_prefix}*')
        }

        result_keys_chunks = make_chunks(iterable=result_keys, size=batch_size)
        for result_keys in result_keys_chunks:
            results = [self.serializer.loads(self.connection.get(result_key)) for result_key in result_keys]

            yield BatchResult(results)

    def enqueue_notification(self, notification: 'Notification') -> bool:
        """Добавление в очередь уведомления."""
        pipe = self.connection.pipeline()
        pipe.sadd(self.queues_keys, self.key)

        notification_key = self.get_notification_key(notification.id)

        pipe.set(notification_key, self.serializer.dumps(notification), ex=notification.ttl)
        pipe.lpush(self.key, notification.id)

        pipe.execute()

        self.log.debug(f'Уведомление {notification.id} помещено в очередь {self.key}')

        return True

    def _get_notification_from_redis(self, notification_id: str) -> Optional['Notification']:
        """Возвращает уведомление из Redis."""
        notification_key = self.get_notification_key(notification_id)
        raw_notification = self.connection.get(notification_key)
        if raw_notification:
            return self.serializer.loads(raw_notification)

    def _lmove(self, consumer_id: str) -> bytes:
        """Возвращает значение из очереди используя команду в зависимости от версии Redis."""
        if get_redis_version(self.connection) >= (7, 0, 0):
            lmove = partial(
                self.connection.lmove, self.key, self.get_processing_queue_key(consumer_id), src='RIGHT', dest='LEFT'
            )
        else:
            lmove = partial(self.connection.rpoplpush, self.key, self.get_processing_queue_key(consumer_id))

        return lmove()

    def dequeue_notification(self, consumer_id: str) -> Optional['Notification']:
        """Возвращает из очереди уведомление."""
        notification_id = self._lmove(consumer_id)
        if not notification_id:
            return None

        return self._get_notification_from_redis(as_text(notification_id))

    def dequeue_notifications(self, count: int, consumer_id: str) -> List['Notification']:
        """Возвращает из очереди перечень уведомлений."""
        notifications = []
        for _ in range(count):
            notification_id = self._lmove(consumer_id)
            if not notification_id:
                break

            notification = self._get_notification_from_redis(as_text(notification_id))
            if notification:
                notifications.append(notification)

        return notifications

    def maintain_processing_queue(self, consumer_id: str) -> Tuple[int, int]:
        """Обслуживание processing очереди.

        В случае, если в processing очереди "застряли" сообщения, они возвращаются
        в основную очередь для повторной обработки.
        """
        returned, removed = 0, 0
        processing_queue_key = self.get_processing_queue_key(consumer_id)

        while True:
            notification_id = self.connection.lpop(processing_queue_key)
            if not notification_id:
                break
            if self.connection.exists(self.get_notification_key(as_text(notification_id))):
                self.connection.rpush(self.key, notification_id)
                returned += 1
            else:
                removed += 1

        return returned, removed

    def push_to_queue(self, ids: List[str], ttl_reduce_factor: int = 0) -> int:
        """Возвращает указанные id уведомлений в очередь."""
        pushed_count = 0
        for id in ids:
            notification_key = self.get_notification_key(id)
            ttl = self.connection.ttl(notification_key)
            if ttl > 0:
                self.connection.lpush(self.key, id)
                pushed_count += 1
                if ttl_reduce_factor:
                    self.connection.expire(notification_key, int(ttl / ttl_reduce_factor))

        return pushed_count

    def clean_processing_queue(self, consumer_id: str) -> bool:
        """Удаляет id уведомлений из processing очереди."""
        processing_queue_key = self.get_processing_queue_key(consumer_id)
        if self.connection.llen(processing_queue_key) == 0:
            return True

        return bool(self.connection.delete(processing_queue_key))

    @property
    def connection_info(self) -> str:
        """Информация об используемом соединении."""
        version = '.'.join(map(str, get_redis_version(self.connection)))
        kwargs = self.connection.connection_pool.connection_kwargs
        host = kwargs['host']
        port = kwargs['port']
        db = kwargs['db']

        return f'Redis {version} on {host}:{port}/{db}'
