from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://blog_user:blog_pass@db:5432/blog"
    SECRET_KEY: str = "changeme-secret-key"
    APP_NAME: str = "Blog REST API"

    class Config:
        env_file = ".env"


settings = Settings()