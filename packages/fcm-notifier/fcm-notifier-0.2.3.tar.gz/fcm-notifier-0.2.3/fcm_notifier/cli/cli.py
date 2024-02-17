import sys

import click
from redis.exceptions import (
    ConnectionError,
)

from fcm_notifier import (
    __version__ as version,
    settings,
)
from fcm_notifier.consts import (
    MAX_MESSAGES_PER_BATCH,
)
from fcm_notifier.helpers import (
    get_redis_connection,
)
from fcm_notifier.queue import (
    RedisQueue,
)
from fcm_notifier.sender import (
    NotificationFCMSender,
)
from fcm_notifier.worker import (
    Worker,
)


@click.group()
@click.version_option(version)
def main():
    pass


@main.command
def worker():
    queue = RedisQueue(connection=get_redis_connection())
    sender = NotificationFCMSender()

    worker = Worker(
        name='main',
        queue=queue,
        sender=sender,
        logging_level=settings.LOGGING_LEVEL,
    )
    try:
        worker.work(
            batch_size=MAX_MESSAGES_PER_BATCH,
        )
    except ConnectionError as e:
        worker.log.error(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
