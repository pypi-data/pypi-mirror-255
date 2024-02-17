import base64
from enum import StrEnum

import pydantic
from pydantic import ConfigDict
from pylogram.session.internals import DataCenter

from ks_session_manager.utils import phone


class PydanticBaseModel(pydantic.BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class AccountType(StrEnum):
    TELETHON = 'TELETHON'
    PYLOGRAM = 'PYROGRAM'


class TelegramPlatform(StrEnum):
    IOS = 'IOS'
    MACOS = 'MACOS'
    ANDROID = 'ANDROID'
    DESKTOP_WINDOWS = 'DESKTOP_WINDOWS'
    DESKTOP_MACOS = 'DESKTOP_MACOS'
    DESKTOP_LINUX = 'DESKTOP_LINUX'
    WEB = 'WEB'


class SessionMetadata(PydanticBaseModel):
    user_id: int | None = pydantic.Field(0, alias='id')
    phone_number: str | None = pydantic.Field(None, alias='phone')
    two_factor_password: str | None = pydantic.Field(None, alias='twoFA')
    api_id: int = pydantic.Field(..., alias='app_id')
    api_hash: str = pydantic.Field(..., alias='app_hash')

    # Device settings
    app_version: str | None = None
    device_model: str | None = pydantic.Field(None, alias='device')
    system_version: str | None = pydantic.Field(None, alias='sdk')
    lang_code: str = 'en'
    system_lang_code: str = 'en-US'
    lang_pack: str | None = ''
    system_lang_pack: str | None = ''

    # Network settings
    ipv6: bool | None = False

    # Account info
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    avatar: str | None = None
    sex: int | None = None
    is_premium: bool | None = False

    # Timings
    register_time: int | float | None = None
    last_check_time: int | float | None = None

    # Tokens
    device_token: str | None = None
    device_token_secret: str | None = None
    device_secret: str | None = None
    signature: str | None = None
    certificate: str | None = None
    safetynet: str | None = None

    proxy: list[int | bool | str] | None = None

    @pydantic.field_validator('phone_number', mode='before')
    @classmethod
    def normalize_phone_number(cls, phone_number: str | None) -> str | None:
        return phone.clean_phone_number(phone_number) if phone_number else None


class SessionPeer(PydanticBaseModel):
    id: int
    access_hash: int
    phone_number: str | None = None
    username: str | None = None

    @property
    def peer_type(self) -> str:
        return 'bot' if bool(self.username) and self.username.endswith('bot') else 'user'


class SessionData(PydanticBaseModel):
    dc_id: int
    auth_key: bytes
    user_id: int | None = None
    is_bot: bool = False
    test_mode: bool = False
    server_address: str | None = None
    server_port: int | None = None
    takeout_id: int | None = None

    @pydantic.field_serializer('auth_key', return_type=str, when_used='json')
    def serialize_dt(self, auth_key: bytes, _info) -> str:
        return base64.standard_b64encode(auth_key).decode()

    @pydantic.model_validator(mode='after')
    def check_passwords_match(self) -> 'SessionData':
        if self.server_address is None or self.server_port is None:
            self.server_address, self.server_port = DataCenter(self.dc_id, self.test_mode, False, False)

        return self


class SessionProxy(PydanticBaseModel):
    scheme: str = "http"
    hostname: str
    port: int
    username: str | None = None
    password: str | None = None

    def to_telethon_format(self) -> dict:
        return {
            'proxy_type': self.scheme,
            'addr': self.hostname,
            'port': self.port,
            'username': self.username,
            'password': self.password,
        }

    def to_pyrogram_format(self) -> dict:
        return {
            'scheme': self.scheme,
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'password': self.password
        }


class SessionUserInfo(PydanticBaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    phone_number: str | None = None
    is_premium: bool = False
