from pathlib import Path
from typing import Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    environment: str = "development"
    secret_key: SecretStr | None = None
    storage_dir: Path = BACKEND_ROOT / "storage"
    database_url: str | None = None
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ]
    )
    access_token_minutes: int = Field(default=15, ge=1, le=60)
    refresh_token_days: int = Field(default=7, ge=1, le=90)
    bootstrap_admin_username: str | None = None
    bootstrap_admin_email: str | None = None
    bootstrap_admin_password: SecretStr | None = None
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int | None = Field(default=587, alias="SMTP_PORT", ge=1, le=65535)
    smtp_tls: bool = Field(default=True, alias="SMTP_TLS")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: SecretStr | None = Field(default=None, alias="SMTP_PASSWORD")
    notifications_recipient: str | None = Field(default=None, alias="NOTIFICATIONS_RECIPIENT")
    remember_me_enabled: bool = Field(default=False, alias="REMEMBER_ME_ENABLED")

    @model_validator(mode="after")
    def validate_bootstrap_admin(self) -> Self:
        bootstrap_values = (
            self.bootstrap_admin_username,
            self.bootstrap_admin_email,
            self.bootstrap_admin_password,
        )
        if any(bootstrap_values) and not all(bootstrap_values):
            raise ValueError(
                "Bootstrap administrator username, email, and password must be set together."
            )
        if (
            self.bootstrap_admin_password is not None
            and len(self.bootstrap_admin_password.get_secret_value()) < 14
        ):
            raise ValueError("Bootstrap administrator password must contain at least 14 characters.")
        return self

    @property
    def is_production(self) -> bool:
        return self.environment.casefold() == "production"


def get_settings() -> Settings:
    return Settings()
