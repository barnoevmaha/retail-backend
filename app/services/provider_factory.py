from app.core.config import settings
from app.services.email_provider import EmailProvider, MockEmailProvider
from app.services.resend_provider import ResendEmailProvider
from app.services.sms_service import SmsProvider, MockSmsProvider, EskizSmsProvider, TwilioSmsProvider
from sqlalchemy.orm import Session


def get_email_provider() -> EmailProvider:
    match settings.email_provider:
        case "resend":
            return ResendEmailProvider()
        case "mock":
            return MockEmailProvider()
    raise ValueError(f"Unknown EMAIL_PROVIDER: {settings.email_provider!r} (use 'mock' or 'resend')")


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
