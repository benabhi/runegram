
from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr

    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    # Redis
    redis_host: str
    redis_port: int
    redis_db: int

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()