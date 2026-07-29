from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> bool:
        ...


class MockEmailProvider(EmailProvider):
    def send(self, recipient: str, subject: str, body: str) -> bool:
        print(f"[EMAIL MOCK] To: {recipient}, Subject: {subject}, Body: {body}")
        return True
