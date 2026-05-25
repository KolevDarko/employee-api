from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    employee_api_base_url: str = ""
    employee_api_client_id: str = ""
    employee_api_client_secret: str = ""
    employee_api_username: str = ""
    employee_api_password: str = ""
    employee_api_grant_type: str = "password"
    auth_header_name: str = "Access-Token"

    database_url: str = "sqlite+aiosqlite:///./dev.db"
    database_url_sync: str = "sqlite:///./dev.db"

    @computed_field
    @property
    def employee_api_token_url(self) -> str:
        return f"{self.employee_api_base_url.rstrip('/')}/api/token"

    @computed_field
    @property
    def employee_api_employees_url(self) -> str:
        return f"{self.employee_api_base_url.rstrip('/')}/api/employee/list"


@lru_cache
def get_settings() -> Settings:
    return Settings()
