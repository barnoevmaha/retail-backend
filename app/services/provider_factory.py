from app.core.config import settings
from app.services.email_provider import EmailProvider, MockEmailProvider, SMTPEmailProvider
from app.services.sms_service import SmsProvider, MockSmsProvider, EskizSmsProvider, TwilioSmsProvider
from sqlalchemy.orm import Session


def get_email_provider() -> EmailProvider:
    if settings.smtp_host and settings.smtp_username:
        return SMTPEmailProvider()
    return MockEmailProvider()


def get_sms_provider() -> SmsProvider:
    match settings.sms_provider:
        case "eskiz":
            return EskizSmsProvider()
        case "twilio":
            return TwilioSmsProvider()
    return MockSmsProvider()


def get_sms_service(db: Session):
    from app.services.sms_service import SmsService
    return SmsService(db, get_sms_provider())
