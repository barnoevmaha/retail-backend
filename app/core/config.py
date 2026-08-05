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

    # Email delivery — "mock" (prints, no sending) or "resend"
    email_provider: str = "mock"
    resend_api_key: str = ""
    email_from: str = ""

    # Translation (auto-translate UI strings EN -> RU/UZ; provider auto-detected by key)
    translation_provider: str = ""  # gemini | openai | deepl | google | "" (auto)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    deepl_api_key: str = ""
    google_translate_api_key: str = ""

    # Eskiz SMS
    eskiz_email: str = ""
    eskiz_password: str = ""
    eskiz_from: str = ""

    # Twilio SMS
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone: str = ""

    # Super admin bootstrap — no hardcoded credentials. Must be set via env.
    # The super admin is created on first boot only if these are provided.
    super_admin_email: str = ""
    super_admin_password: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
