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

    class Config:
        env_file = ".env"


settings = Settings()
