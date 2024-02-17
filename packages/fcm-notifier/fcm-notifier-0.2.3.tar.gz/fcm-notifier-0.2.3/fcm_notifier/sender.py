from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
)

from firebase_admin import (
    initialize_app,
    messaging,
)
from firebase_admin.exceptions import (
    InvalidArgumentError,
)
from firebase_admin.messaging import (
    UnregisteredError,
)
from google.auth.exceptions import (
    DefaultCredentialsError,
)

from fcm_notifier.results import (
    BatchResult,
    Result,
    ResultStatus,
)


if TYPE_CHECKING:
    from firebase_admin import (
        App,
    )

    from fcm_notifier.notification import (
        Notification,
        NotificationPayload,
    )


class FCMSender(ABC):

    def __init__(self, app: Optional['App'] = None):
        """Инициализация."""
        self._app = app or initialize_app()

    @property
    def project_id(self):
        """Firebase project ID связанный с приложением App."""
        try:
            project_id = self._app.project_id
        except DefaultCredentialsError:
            project_id = None

        return project_id

    @abstractmethod
    def send_all(self, *args, **kwargs) -> BatchResult:
        """Отправка пачки сообщений."""


class NotificationFCMSender(FCMSender):

    @staticmethod
    def _compose_fcm_message(payload: 'NotificationPayload', token: str) -> messaging.Message:
        """Формирование Message для отправки в FCM."""
        return messaging.Message(
            notification=messaging.Notification(
                title=payload.title,
                body=payload.body,
                image=payload.image,
            ),
            token=token,
        )

    def send_all(
        self,
        notifications: List['Notification'],
        dry_run: bool = False,
    ) -> BatchResult:
        """Отправка пачки сообщений."""
        messages = [self._compose_fcm_message(n.payload, n.token) for n in notifications]
        # TODO: обработка UnknownError
        batch_response = messaging.send_each(messages, dry_run=dry_run, app=self._app)

        results = []
        for idx, response in enumerate(batch_response.responses):
            if response.success:
                status = ResultStatus.SUCCESSFUL
                exc_code = ''
                exc_string = ''
            else:
                if isinstance(response.exception, (UnregisteredError, InvalidArgumentError)):
                    status = ResultStatus.INVALID_TOKEN
                else:
                    status = ResultStatus.FAILED

                exc_code = response.exception.code
                exc_string = (
                    f'{response.exception.__class__.__name__}: {exc_code} - "{response.exception}"'
                )

            results.append(
                Result(
                    id=notifications[idx].id,
                    token=notifications[idx].token,
                    status=status,
                    fcm_message_id=response.message_id or '',
                    exc_code=exc_code,
                    exc_string=exc_string,
                )
            )

        return BatchResult(results)
