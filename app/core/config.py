from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://clothes_shop:clothes_shop@localhost:5432/clothes_shop"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    cors_origins: str = "*"
    frontend_url: str = ""
    admin_url: str = ""
    upload_dir: str = "uploads"
    sms_provider: str = "mock"
    telegram_bot_token: str = ""
    refresh_token_expire_days: int = 30
    company_name: str = "Clothes Shop"

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True

    # Eskiz SMS
    eskiz_email: str = ""
    eskiz_password: str = ""
    eskiz_from: str = ""

    # Twilio SMS
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone: str = ""

    # Seed credentials — env vars in production, safe placeholders otherwise
    super_admin_email: str = "admin@example.com"
    super_admin_password: str = "ChangeMe123!"
    manager_email: str = "manager@example.com"
    manager_password: str = "ChangeMe123!"
    cashier_email: str = "cashier@example.com"
    cashier_password: str = "ChangeMe123!"
    warehouse_email: str = "warehouse@example.com"
    warehouse_password: str = "ChangeMe123!"

    class Config:
        env_file = ".env"


settings = Settings()
