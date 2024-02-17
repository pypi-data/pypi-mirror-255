import asyncio
import logging
import random
import re
from datetime import datetime
from datetime import timezone
from pathlib import Path

import telethon
import telethon.sessions

from ks_session_manager.errors import SigningInDisabledError
from ks_session_manager.types import SessionMetadata
from ks_session_manager.types import SessionProxy

logger = logging.getLogger(__name__)


class TelethonClient(telethon.TelegramClient):
    def __init__(
            self,
            data: SessionMetadata,
            *,
            session_path: str | Path | None = None,
            session_storage: telethon.sessions.Session | None = None,
            proxy: SessionProxy | None = None,
            sign_in_enabled: bool = True,
            # Passthrough
            connection: type[telethon.network.Connection] = telethon.network.ConnectionTcpFull,
            use_ipv6: bool = False,
            local_addr: str | tuple = None,
            timeout: int = 10,
            request_retries: int = 5,
            connection_retries: int = 5,
            retry_delay: int = 1,
            auto_reconnect: bool = True,
            sequential_updates: bool = False,
            flood_sleep_threshold: int = 60,
            raise_last_call_error: bool = False,
            loop: asyncio.AbstractEventLoop = None,
            base_logger: str | logging.Logger = None,
            receive_updates: bool = True,
            entity_cache_limit: int = 5000
    ):
        if not bool(session_path) and not bool(session_storage):
            raise ValueError("Either session_path or session_storage must be provided")

        if bool(session_path) and bool(session_storage):
            raise ValueError("Either session_path or session_storage must be provided, not both")

        if bool(session_path):
            session = str(Path(session_path).resolve())
        else:
            session = session_storage

        self.session: telethon.sessions.Session | None = None
        self.me: telethon.types.User | None = None
        self.session_metadata: SessionMetadata = data
        self.sign_in_enabled = sign_in_enabled

        super().__init__(
            session,
            data.api_id,
            data.api_hash,
            proxy=proxy.to_telethon_format() if bool(proxy) else None,
            device_model=data.device_model,
            system_version=data.system_version,
            app_version=data.app_version,
            lang_code=data.lang_code,
            system_lang_code=data.system_lang_code,
            # Other
            catch_up=False,
            # Passthrough
            connection=connection,
            use_ipv6=use_ipv6,
            local_addr=local_addr,
            timeout=timeout,
            request_retries=request_retries,
            connection_retries=connection_retries,
            retry_delay=retry_delay,
            auto_reconnect=auto_reconnect,
            sequential_updates=sequential_updates,
            flood_sleep_threshold=flood_sleep_threshold,
            raise_last_call_error=raise_last_call_error,
            loop=loop,
            base_logger=base_logger,
            receive_updates=receive_updates,
            entity_cache_limit=entity_cache_limit
        )
        # noinspection PyUnresolvedReferences
        self._init_request.lang_pack = data.lang_pack

    async def send_code_request(
            self,
            phone: str,
            *,
            force_sms: bool = False,
            _retry_count: int = 0
    ) -> telethon.types.auth.SentCode:
        result: telethon.types.auth.SentCode = await super().send_code_request(
            phone,
            force_sms=force_sms,
            _retry_count=_retry_count
        )
        logger.info(f"Code sent to {phone}. Code type is {result.type}")

        if not self.sign_in_enabled:
            raise SigningInDisabledError(code_type=str(result.type))

        return result

    async def _on_login(self, user: telethon.types.User | None):
        self.me = await super()._on_login(user)
        logger.info(f"Signed in as {self.me.id}: {self.me.phone}")

    async def export_session_string(self) -> str:
        storage = telethon.sessions.StringSession()
        storage.set_dc(
            self.session.dc_id,
            self.session.server_address,
            self.session.port
        )
        storage.auth_key = self.session.auth_key
        return storage.save()

    async def retrieve_telegram_code(self, *, request_date: datetime = None, timeout: int = 60) -> str | None:
        """
        Retrieves the verification code from a Telegram message.

        Parameters:
        - request_date: Optional datetime parameter representing the date and time from which the code should be retrieved. Defaults to the current date and time in UTC if not provided.
        - timeout: Optional integer parameter representing the maximum time in seconds to wait for a code to be retrieved. Defaults to 60 seconds if not provided.

        Returns:
        - A string representing the retrieved verification code if successful.
        - None if no code is found within the specified timeout period.

        """
        if request_date is None:
            request_date = datetime.now(tz=timezone.utc)

        async with asyncio.timeout(timeout):
            while True:
                async for message in self.iter_messages(777000, limit=1):
                    if int(message.date.timestamp()) < int(request_date.timestamp()):
                        break

                    try:
                        return re.findall(r'[0-9]{5}', message.text, flags=re.MULTILINE)[0]
                    except IndexError:
                        logging.warning("Found new Telegram message but no code received")

                await asyncio.sleep(random.uniform(1, 3))
