from abc import ABC, abstractmethod
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.sms import SmsLog


class SmsProvider(ABC):
    @abstractmethod
    def send(self, phone: str, message: str) -> bool:
        ...


class MockSmsProvider(SmsProvider):
    def send(self, phone: str, message: str) -> bool:
        print(f"[SMS MOCK] To: {phone}, Message: {message}")
        return True


class EskizSmsProvider(SmsProvider):
    _token: str | None = None

    def _login(self) -> str:
        data = urlencode({"email": settings.eskiz_email, "password": settings.eskiz_password}).encode()
        req = Request("https://notify.eskiz.uz/api/auth/login", data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            return body["data"]["token"]

    def _ensure_token(self):
        if not self._token:
            self._token = self._login()

    def send(self, phone: str, message: str) -> bool:
        try:
            self._ensure_token()
            data = urlencode({"mobile_phone": phone, "message": message, "from": settings.eskiz_from}).encode()
            req = Request("https://notify.eskiz.uz/api/message/sms/send", data=data, method="POST")
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            req.add_header("Authorization", f"Bearer {self._token}")
            with urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                return result.get("status") == "success"
        except Exception as e:
            print(f"[ESKIZ ERROR] {e}")
            return False


class TwilioSmsProvider(SmsProvider):
    def send(self, phone: str, message: str) -> bool:
        try:
            data = urlencode({"To": phone, "From": settings.twilio_phone, "Body": message}).encode()
            auth = f"{settings.twilio_account_sid}:{settings.twilio_auth_token}"
            b64auth = __import__("base64").b64encode(auth.encode()).decode()
            req = Request(f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json",
                          data=data, method="POST")
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            req.add_header("Authorization", f"Basic {b64auth}")
            with urlopen(req, timeout=10) as resp:
                return resp.status == 201
        except Exception as e:
            print(f"[TWILIO ERROR] {e}")
            return False


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
