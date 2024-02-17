import pathlib

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=".env", extra='ignore')

    SMARTPROXY_USERNAME: str | None = None
    SMARTPROXY_PASSWORD: str | None = None
    SESSIONS_DIR: pathlib.Path = pathlib.Path.cwd() / '.sessions'

    # noinspection PyPep8Naming
    @property
    def PYLOGRAM_WORKDIR(self) -> pathlib.Path:
        return self.SESSIONS_DIR / 'pylogram'

    # noinspection PyPep8Naming
    @property
    def TELETHON_WORKDIR(self) -> pathlib.Path:
        return self.SESSIONS_DIR / 'telethon'


env = Settings()
