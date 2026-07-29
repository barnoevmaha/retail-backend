from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, skip: int = 0, limit: int = 50, channel: str | None = None, status: str | None = None) -> list[Notification]:
        query = self.db.query(Notification)
        if channel:
            query = query.filter(Notification.channel == channel)
        if status:
            query = query.filter(Notification.status == status)
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, id: int) -> Notification | None:
        return self.db.query(Notification).filter(Notification.id == id).first()

    def create(self, **kwargs) -> Notification:
        n = Notification(**kwargs)
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return n

    def update(self, notification: Notification, **kwargs) -> Notification:
        for k, v in kwargs.items():
            setattr(notification, k, v)
        self.db.commit()
        self.db.refresh(notification)
        return notification
