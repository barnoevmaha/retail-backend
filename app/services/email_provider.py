from abc import ABC, abstractmethod
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


class EmailProvider(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> bool:
        ...


def _wrap_html(body: str) -> str:
    code_match = re.search(r"(\d{6})", body)
    code = code_match.group(1) if code_match else ""
    lines = body.strip().split("\n")
    paragraphs = "".join(f"<p style=\"margin:0 0 12px;font-size:14px;color:#374151;line-height:1.6\">{l}</p>" for l in lines)
    code_block = f"<div style=\"background:#f9fafb;border-radius:8px;padding:16px;letter-spacing:8px;font-size:32px;font-weight:700;color:#111827;font-family:monospace;text-align:center;margin:16px 0\">{code}</div>" if code else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:40px 16px">
<table width="400" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08)">
<tr><td style="padding:32px 32px 0" align="center">
<h1 style="margin:0;font-size:20px;font-weight:600;color:#111827">{'Verify your account' if 'verification' in body.lower() or 'code' in body.lower() else ''}</h1>
</td></tr>
<tr><td style="padding:24px 32px" align="center">
{code_block}{paragraphs}
<p style="margin:16px 0 0;font-size:12px;color:#9ca3af">{'This code expires in 10 minutes.' if code else ''}</p>
</td></tr>
<tr><td style="padding:0 32px 32px" align="center">
<p style="margin:0;font-size:12px;color:#9ca3af">If you did not request this, you can safely ignore this email.</p>
</td></tr>
</table>
</td></tr></table>
</body>
</html>"""


class MockEmailProvider(EmailProvider):
    def send(self, recipient: str, subject: str, body: str) -> bool:
        print(f"[EMAIL MOCK] To: {recipient}, Subject: {subject}, Body: {body}")
        return True

import traceback

class SMTPEmailProvider(EmailProvider):
    def send(self, recipient: str, subject: str, body: str) -> bool:
        html = _wrap_html(body)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = recipient
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html, "html"))
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.sendmail(settings.smtp_from, [recipient], msg.as_string())
            return True
        except Exception as e:
            print("========== SMTP ERROR ==========")
            traceback.print_exc()
            print("HOST:", settings.smtp_host)
            print("PORT:", settings.smtp_port)
            print("TLS:", settings.smtp_use_tls)
            print("USER:", settings.smtp_username)
            print("===============================")
            return False
