from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://auth_user:auth_pass@auth_db:5432/auth_db"
    SECRET_KEY: str = "changeme-secret-key"
    APP_NAME: str = "Auth Service"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 2
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100


    class Config:
        env_file = ".env"


settings = Settings()