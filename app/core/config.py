from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Фонд поддержки котов QRKot'
    description: str = (
        'Сервис для благотворительного фонда QRKot: сбор пожертвований '
        'на целевые проекты помощи кошкам, кошечкам и котятам.'
    )
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    first_superuser_email: EmailStr | None = None
    first_superuser_password: str | None = None

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
