from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = True

    TELEMT_API_URL: str = "http://localhost:9095/v1"
    TELEMT_AUTH_HEADER: str = "mysecret"

    PROXY_HOST: str = "YOUR_PROXY_HOST"
    PROXY_PORT: int = 443
    TLS_DOMAIN: str = "google.com"

    # Лимит IP на один ключ (по умолчанию 1)
    MAX_IPS_PER_KEY: int = 1

    MANAGEMENT_API_KEY: str = "change_me_in_env"

    DATABASE_URL: str = "sqlite+aiosqlite:///./telemt_keys.db"
    REDIS_URL: str = "redis://localhost:6370/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def generate_proxy_url(username: str, secret: str) -> str:
    domain_hex = settings.TLS_DOMAIN.encode().hex()
    full_secret = f"ee{secret}{domain_hex}"
    return f"tg://proxy?server={settings.PROXY_HOST}&port={settings.PROXY_PORT}&secret={full_secret}"
