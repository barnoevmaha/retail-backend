from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.notification_repo import NotificationRepository


class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, title: str | None, message: str) -> bool:
        ...


class MockSmsSender(NotificationSender):
    def send(self, recipient: str, title: str | None, message: str) -> bool:
        print(f"[SMS] To: {recipient}, Msg: {message}")
        return True


class MockEmailSender(NotificationSender):
    def send(self, recipient: str, title: str | None, message: str) -> bool:
        print(f"[EMAIL] To: {recipient}, Subject: {title}, Body: {message}")
        return True


class MockTelegramSender(NotificationSender):
    def send(self, recipient: str, title: str | None, message: str) -> bool:
        print(f"[TELEGRAM] To: {recipient}, Msg: {message}")
        return True


class MockPushSender(NotificationSender):
    def send(self, recipient: str, title: str | None, message: str) -> bool:
        print(f"[PUSH] Device: {recipient}, Title: {title}, Msg: {message}")
        return True


CHANNEL_SENDERS: dict[str, NotificationSender] = {
    "sms": MockSmsSender(),
    "email": MockEmailSender(),
    "telegram": MockTelegramSender(),
    "push": MockPushSender(),
}


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def send(self, channel: str, recipient: str, message: str, title: str | None = None, user_id: int | None = None) -> NotificationSender:
        sender = CHANNEL_SENDERS.get(channel)
        if not sender:
            raise ValueError(f"Unknown channel: {channel}")

        notification = self.repo.create(
            user_id=user_id,
            channel=channel,
            title=title,
            message=message,
            status="pending",
            recipient=recipient,
        )

        try:
            success = sender.send(recipient, title, message)
            status = "sent" if success else "failed"
        except Exception:
            status = "failed"

        self.repo.update(
            notification,
            status=status,
            sent_at=datetime.now(timezone.utc) if status == "sent" else None,
        )
        return notification

    def list(self, channel: str | None = None, status: str | None = None, skip: int = 0, limit: int = 50):
        return self.repo.list_all(skip, limit, channel, status)

    def mark_read(self, notification_id: int):
        n = self.repo.get_by_id(notification_id)
        if n:
            self.repo.update(n, read_at=datetime.now(timezone.utc))
        return n
