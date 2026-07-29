from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.sms import SmsLog


class SmsProvider(ABC):
    @abstractmethod
    def send(self, phone: str, message: str) -> bool:
        ...


class MockSmsProvider(SmsProvider):
    def send(self, phone: str, message: str) -> bool:
        print(f"[SMS MOCK] To: {phone}, Message: {message}")
        return True


class SmsService:
    def __init__(self, db: Session, provider: SmsProvider | None = None):
        self.db = db
        self.provider = provider or MockSmsProvider()

    def send(self, phone: str, message: str) -> bool:
        success = self.provider.send(phone, message)
        self.db.add(SmsLog(
            phone=phone,
            message=message,
            status="sent" if success else "failed",
            provider=self.provider.__class__.__name__,
        ))
        self.db.commit()
        return success

    def send_order_confirmed(self, phone: str, order_id: int):
        self.send(phone, f"Order #{order_id} confirmed. Thank you for your purchase!")

    def send_ready_for_pickup(self, phone: str, order_id: int):
        self.send(phone, f"Order #{order_id} is ready for pickup!")

    def send_order_delivered(self, phone: str, order_id: int):
        self.send(phone, f"Order #{order_id} has been delivered. Thank you!")

    def send_promotion(self, phone: str, message: str):
        self.send(phone, message)
