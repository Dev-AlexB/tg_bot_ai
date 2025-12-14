from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseModel):
    token: str


class DatabaseSettings(BaseModel):
    db: str
    host: str
    port: int
    user: str
    password: str


class LoggSettings(BaseModel):
    level: str
    format: str


class Config(BaseSettings):
    bot: BotSettings
    postgres: DatabaseSettings
    log: LoggSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="_",
        extra="ignore",
    )


config = Config()
