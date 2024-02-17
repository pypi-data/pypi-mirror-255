import logging
import sys
from typing import (
    Tuple,
    Union,
)

from redis import (
    Redis,
    ResponseError,
)

from fcm_notifier import (
    settings,
)
from fcm_notifier.consts import (
    DEFAULT_LOGGING_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
)


def get_redis_connection() -> Redis:
    """Возвращает соединение с Redis."""
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
    )


def get_redis_version(connection: 'Redis') -> Tuple[int, int, int]:
    """Возвращает кортеж с версией сервера Redis."""
    try:
        version = getattr(connection, '__redis_server_version', None)
        if not version:
            version = tuple([int(n) for n in connection.info('server')['redis_version'].split('.')[:3]])
            setattr(connection, '__redis_server_version', version)
    except ResponseError:
        version = (0, 0, 0)

    return version


def setup_log_handlers(
    level: Union[int, str, None] = None,
    date_format: str = DEFAULT_LOGGING_DATE_FORMAT,
    log_format: str = DEFAULT_LOGGING_FORMAT,
    name: str = 'fcm_notifier.worker',
):
    """Настройка обработчиков логирования."""
    logger = logging.getLogger(name)

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(lambda record: record.levelno < logging.ERROR)
    error_handler = logging.StreamHandler(stream=sys.stderr)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(lambda record: record.levelno >= logging.ERROR)
    logger.addHandler(handler)
    logger.addHandler(error_handler)

    if level is not None:
        logger.setLevel(level if isinstance(level, int) else level.upper())
