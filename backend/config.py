from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    # Auth
    jwt_secret: str = "dev-only-secret"
    jwt_alg: str = "HS256"
    jwt_expire_minutes: int = 480

    # Supabase
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    # Supabase Storage
    supabase_storage_bucket: str = "evidence"

    # Featherless AI
    featherless_api_key: str | None = None
    featherless_model: str = "meta-llama/Meta-Llama-3.1-70B-Instruct"
    ai_cache_ttl_days: int = 30

    # Vision OCR
    google_application_credentials: str | None = None

    # Contradiction engine
    walk_kmh: float = 5.0
    drive_urban_kmh: float = 60.0
    drive_highway_kmh: float = 100.0
    transit_kmh: float = 40.0
    suspicious_multiplier: float = 1.5
    cctv_gap_threshold_min: float = 15.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
