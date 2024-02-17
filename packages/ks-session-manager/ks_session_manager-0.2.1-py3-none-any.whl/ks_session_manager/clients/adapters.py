import abc

from ks_session_manager.clients import PylogramClient
from ks_session_manager.clients import TelethonClient
from ks_session_manager.types import SessionUserInfo


class BaseTelegramAdapter(abc.ABC):
    @property
    @abc.abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_info(self) -> SessionUserInfo:
        raise NotImplementedError

    @abc.abstractmethod
    async def start(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def stop(self):
        raise NotImplementedError


class TelethonTelegramAdapter(BaseTelegramAdapter):
    def __init__(self, client: TelethonClient):
        self.client = client

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected()

    async def get_user_info(self) -> SessionUserInfo:
        if not self.is_connected:
            raise RuntimeError('Client is not connected')

        return SessionUserInfo(
            id=self.client.me.id,
            first_name=self.client.me.first_name,
            last_name=self.client.me.last_name,
            username=self.client.me.username,
            phone_number=self.client.me.phone,
            is_premium=self.client.me.premium,
        )

    async def start(self):
        # noinspection PyUnresolvedReferences
        await self.client.start()

    async def stop(self):
        await self.client.disconnect()


class PylogramTelegramAdapter(BaseTelegramAdapter):
    def __init__(self, client: PylogramClient):
        self.client = client

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected

    async def get_user_info(self) -> SessionUserInfo:
        if not self.is_connected:
            raise RuntimeError('Client is not connected')

        return SessionUserInfo(
            id=self.client.me.id,
            first_name=self.client.me.first_name,
            last_name=self.client.me.last_name,
            username=self.client.me.username,
            phone_number=self.client.me.phone_number,
            is_premium=self.client.me.is_premium,
        )

    async def start(self):
        # noinspection PyUnresolvedReferences
        await self.client.start()

    async def stop(self):
        await self.client.disconnect()
