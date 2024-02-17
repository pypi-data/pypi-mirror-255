DEFAULT_LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOGGING_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s'
DEFAULT_NOTIFICATION_TTL = 86400  # сутки
DEFAULT_NOTIFICATION_TTL_REDUCE_FACTOR = 2
DEFAULT_RESULT_TTL = 86400  # сутки
DEFAULT_WORKER_IDLE_TIMEOUT = 30  # секунды
DEFAULT_RESULT_BATCH_SIZE = 10_000

# Максимально возможное кол-во сообщений для одновременной отправки через FCM
MAX_MESSAGES_PER_BATCH = 500
