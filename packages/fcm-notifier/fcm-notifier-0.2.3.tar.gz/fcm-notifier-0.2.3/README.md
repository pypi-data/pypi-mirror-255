# Сервис по отправке push-уведомлений через Firebase Cloud Messaging

## Общее описание

fcm-notifier представляет собой сервис, который отдельно запускается в окружении РИС и с заданной 
периодичностью забирает накопившиеся сообщения из очереди, которые пачкой (до 500 штук) отправляет 
на мобильные устройства через FCM backend используя Firebase Admin SDK.

![](img/fcm-notifier-scheme.png)

## Настройка сервиса

Для работы сервиса необходимо в переменных окружения задать две переменные:

Путь до JSON-файла содержащего приватный ключ для доступа к сервисам Google:

    export GOOGLE_APPLICATION_CREDENTIALS=/opt/bars/fcm-notifier/mydiary.json

Путь до директории содержащей файл конфигурации сервиса:

    export FCM_NOTIFIER_CONFIG_DIR=/opt/bars/fcm-notifier/

Файл конфигурации fcm_notifier.conf:

```ini
[redis]
REDIS_HOST = 127.0.0.1
REDIS_PORT = 6379
REDIS_DB = 12
REDIS_PASSWORD =

[logging]
LEVEL = INFO
```

## Запуск сервиса

    $ fcm-notifier worker

## Использование очереди сообщений в РИС

Добавление сообщения в очередь:
```python
from fcm_notifier.helpers import get_redis_connection
from fcm_notifier.notification import Notification, NotificationPayload
from fcm_notifier.queue import RedisQueue


queue = RedisQueue(connection=get_redis_connection())

notification = Notification(
    payload=NotificationPayload(
        title='Test message!',
        body='Message body',
    ),
    token='dsufZwUdSFaeIGFt77aMwm:APA91bHQje7R...',
)

queue.enqueue_notification(notification)
```
