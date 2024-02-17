from __future__ import annotations

from datetime import datetime
from datetime import timezone
from typing import Any

import pylogram

from ks_session_manager.managers.base_manager import BaseSessionFileManager
from ks_session_manager.types import SessionData


class PylogramSessionFileManager(BaseSessionFileManager):
    @property
    def session_file_extension(self) -> str:
        return pylogram.storage.FileStorage.FILE_EXTENSION

    def _get_file_storage(self, *, exists: bool = False) -> pylogram.storage.SQLiteStorage:
        if not exists and self.session_path.exists():
            raise FileExistsError(f"Session storage is already exists in {self.session_path}")

        if exists and not self.session_path.exists():
            raise FileNotFoundError(f"Session storage not found in {self.session_path}")

        if self.session_path.is_dir():
            raise IsADirectoryError(f"Session file path {self.session_path} points to a directory")

        return pylogram.storage.FileStorage(name=self.session_name, workdir=self.workdir)

    async def read_session_storage(self) -> SessionData:
        storage = self._get_file_storage(exists=True)

        await storage.open()
        dc_id = await storage.dc_id()
        user_id = await storage.user_id()
        auth_key = await storage.auth_key()
        is_bot = await storage.is_bot()
        test_mode = await storage.test_mode()
        server_address = None
        server_port = None
        takeout_id = None
        await storage.save()
        await storage.close()

        return SessionData(
            dc_id=dc_id,
            auth_key=auth_key,
            user_id=user_id,
            is_bot=is_bot,
            test_mode=test_mode,
            server_address=server_address,
            server_port=server_port,
            takeout_id=takeout_id,
        )

    async def write_session_storage(self, data: SessionData, *, in_memory: bool = False) -> Any:
        if not bool(data.user_id):
            raise ValueError("user_id must be set in session data")

        if in_memory:
            storage = pylogram.storage.MemoryStorage(self.session_name)
        else:
            storage = self._get_file_storage(exists=False)

        await storage.open()
        await storage.dc_id(data.dc_id)
        await storage.api_id(0)
        await storage.auth_key(data.auth_key)
        await storage.user_id(data.user_id)
        await storage.test_mode(data.test_mode)
        await storage.is_bot(data.is_bot)
        await storage.date(int(datetime.now(timezone.utc).timestamp()))
        await storage.save()
        await storage.close()
        return storage
