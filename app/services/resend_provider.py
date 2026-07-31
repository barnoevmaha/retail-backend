import logging
import time

import resend
from resend.exceptions import RateLimitError, ResendError
from resend.http_client_requests import RequestsClient

from app.core.config import settings
from app.services.email_provider import EmailProvider, _wrap_html

logger = logging.getLogger(__name__)


class ResendEmailError(RuntimeError):
    """Email delivery failed after all retries were exhausted."""


class ResendEmailProvider(EmailProvider):
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 15
    RETRY_DELAY_SECONDS = 1.0

    def __init__(self):
        resend.api_key = settings.resend_api_key
        resend.default_http_client = RequestsClient(timeout=self.TIMEOUT_SECONDS)

    @staticmethod
    def _retryable(e: Exception) -> bool:
        if isinstance(e, RateLimitError):
            return True
        code = getattr(e, "code", None)
        return isinstance(code, int) and code >= 500

    @staticmethod
    def _log_failure(e: Exception, attempt: int) -> None:
        logger.error(
            "Resend email failed (attempt %d/%d): type=%s code=%s message=%s headers=%s",
            attempt, ResendEmailProvider.MAX_RETRIES,
            getattr(e, "error_type", type(e).__name__),
            getattr(e, "code", "?"),
            getattr(e, "message", str(e)),
            getattr(e, "headers", {}),
        )

    def send(self, recipient: str, subject: str, body: str) -> bool:
        params = {
            "from": settings.email_from,
            "to": [recipient],
            "subject": subject,
            "html": _wrap_html(body),
        }
        last_error: Exception | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = resend.Emails.send(params)
                logger.info(
                    "Resend email sent: id=%s to=%s subject=%r (attempt %d)",
                    response.id, recipient, subject, attempt,
                )
                return True
            except Exception as e:
                last_error = e
                self._log_failure(e, attempt)
                if not self._retryable(e) or attempt == self.MAX_RETRIES:
                    break
                time.sleep(self.RETRY_DELAY_SECONDS * attempt)
        raise ResendEmailError(
            f"Email delivery to {recipient!r} failed after {self.MAX_RETRIES} attempts: {last_error}"
        )
