from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import (
    TYPE_CHECKING,
    Optional,
)
from uuid import (
    uuid4,
)

from fcm_notifier import (
    settings,
)
from fcm_notifier.utils import (
    now,
)


if TYPE_CHECKING:
    import datetime


@dataclass
class NotificationPayload:
    """Полезная нагрузка уведомления."""

    title: str = ''
    body: str = ''
    image: Optional[str] = None

    def to_dict(self) -> dict:
        """Преобразование объекта уведомления в словарь с данными."""
        return asdict(self)


@dataclass
class Notification:
    """Push-уведомление."""

    token: str
    payload: 'NotificationPayload'

    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: 'datetime.datetime' = field(default_factory=now)
    ttl: int = settings.NOTIFICATION_TTL

    @classmethod
    def from_dict(cls, d: dict) -> 'Notification':
        """Создание уведомления из словаря с данными."""
        d = d.copy()
        return cls(
            payload=NotificationPayload(**d.pop('payload')),
            **d,
        )

    def to_dict(self) -> dict:
        """Преобразование объекта уведомления в словарь с данными."""
        return asdict(self)
