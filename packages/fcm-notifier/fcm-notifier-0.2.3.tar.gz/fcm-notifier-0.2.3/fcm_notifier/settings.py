import os

from fcm_notifier import (
    config,
)
from fcm_notifier.consts import (
    DEFAULT_NOTIFICATION_TTL,
    DEFAULT_NOTIFICATION_TTL_REDUCE_FACTOR,
    DEFAULT_RESULT_BATCH_SIZE,
    DEFAULT_RESULT_TTL,
    DEFAULT_WORKER_IDLE_TIMEOUT,
)


_CONFIG_FILENAME = 'fcm_notifier.conf'
_CONFIG_DIR_ENV = 'FCM_NOTIFIER_CONFIG_DIR'
_CONFIG_DIR = os.getenv(_CONFIG_DIR_ENV)

if not _CONFIG_DIR:
    _CONFIG_DIR = os.path.dirname(__file__)

CFG_FILENAMES = (
    os.path.join(_CONFIG_DIR, _CONFIG_FILENAME),
)

cfg = config.Config(filenames=CFG_FILENAMES)

REDIS_HOST = cfg.get('redis', 'REDIS_HOST', 'localhost')
REDIS_PORT = cfg.get_int('redis', 'REDIS_PORT', 6379)
REDIS_DB = cfg.get_int('redis', 'REDIS_DB', 0)
REDIS_PASSWORD = cfg.get('redis', 'REDIS_PASSWORD', None)

LOGGING_LEVEL = cfg.get('logging', 'LEVEL', 'INFO')

WORKER_IDLE_TIMEOUT = cfg.get_int('worker', 'IDLE_TIMEOUT', DEFAULT_WORKER_IDLE_TIMEOUT)

NOTIFICATION_TTL = cfg.get_int('queue', 'NOTIFICATION_TTL', DEFAULT_NOTIFICATION_TTL)
NOTIFICATION_TTL_REDUCE_FACTOR = cfg.get_int(
    'queue', 'NOTIFICATION_TTL_REDUCE_FACTOR', DEFAULT_NOTIFICATION_TTL_REDUCE_FACTOR
)
RESULT_TTL = cfg.get_int('queue', 'RESULT_TTL', DEFAULT_RESULT_TTL)
RESULT_BATCH_SIZE = cfg.get_int('queue', 'RESULT_BATCH_SIZE', DEFAULT_RESULT_BATCH_SIZE)
