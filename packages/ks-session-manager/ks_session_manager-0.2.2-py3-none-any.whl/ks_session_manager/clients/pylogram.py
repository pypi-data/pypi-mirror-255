from pathlib import Path

import pylogram

from ks_session_manager.env import env
from ks_session_manager.types import SessionMetadata
from ks_session_manager.types import SessionProxy


class PylogramClient(pylogram.Client):
    def __init__(
            self,
            data: SessionMetadata,
            *,
            session_path: str | Path | None = None,
            session_storage: pylogram.storage.Storage | None = None,
            proxy: SessionProxy | None = None,
            sign_in_enabled: bool = True,  # No-op
            ipv6: bool = False,
            test_mode: bool = False,
            bot_token: str = None,
            session_string: str = None,
            in_memory: bool = None,
            phone_code: str = None,
            password: str = None,
            workers: int = pylogram.Client.WORKERS,
            plugins: dict = None,
            parse_mode: pylogram.enums.ParseMode = pylogram.enums.ParseMode.HTML,
            no_updates: bool = None,
            takeout: bool = None,
            sleep_threshold: int = pylogram.session.Session.SLEEP_THRESHOLD,
            hide_password: bool = False,
            max_concurrent_transmissions: int = pylogram.Client.MAX_CONCURRENT_TRANSMISSIONS,
            ignore_channel_updates_except: list[int] = None,
            message_cache_size: int = 5000,
            first_name: str = None,
            last_name: str = None
    ):
        if not bool(session_path) and not bool(session_storage):
            raise ValueError("Either session_path or session_storage must be provided")

        if bool(session_path) and bool(session_storage):
            raise ValueError("Either session_path or session_storage must be provided, not both")

        if bool(session_path):
            session_path = Path(session_path).resolve()
            session_name = session_path.stem
            workdir = session_path.parent
        else:
            session_name = data.phone_number
            workdir = env.PYLOGRAM_WORKDIR

        super().__init__(
            session_name,
            phone_number=data.phone_number,
            password=password or data.two_factor_password,
            api_id=data.api_id,
            api_hash=data.api_hash,
            app_version=data.app_version,
            device_model=data.device_model,
            system_version=data.system_version,
            lang_code=data.lang_code,
            system_lang_code=data.system_lang_code,
            lang_pack=data.lang_pack,
            # system_lang_pack=data.system_lang_pack,
            proxy=proxy.to_pyrogram_format() if bool(proxy) else None,
            # Passthrough
            session_storage=session_storage,
            ipv6=ipv6,
            test_mode=test_mode,
            bot_token=bot_token,
            session_string=session_string,
            in_memory=in_memory,
            phone_code=phone_code,
            workers=workers,
            workdir=str(workdir),
            plugins=plugins,
            parse_mode=parse_mode,
            no_updates=no_updates,
            takeout=takeout,
            sleep_threshold=sleep_threshold,
            hide_password=hide_password,
            max_concurrent_transmissions=max_concurrent_transmissions,
            ignore_channel_updates_except=ignore_channel_updates_except,
            message_cache_size=message_cache_size,
            first_name=first_name,
            last_name=last_name
        )
        self.session_metadata: SessionMetadata = data
        self.sign_in_enabled = sign_in_enabled
