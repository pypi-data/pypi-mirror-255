from __future__ import annotations

import pathlib

from ks_session_manager.env import env
from ks_session_manager.types import AccountType
from .base_manager import BaseSessionFileManager
from .pylogram_manager import PylogramSessionFileManager
from .telethon_manager import TelethonSessionFileManager


def create_session_manager_of_type(
        account_type: AccountType,
        session_name: str,
        workdir: str | pathlib.Path | None = None
) -> BaseSessionFileManager:
    if account_type == AccountType.TELETHON:
        return TelethonSessionFileManager(session_name=session_name, workdir=workdir or env.TELETHON_WORKDIR)
    elif account_type == AccountType.PYLOGRAM:
        return PylogramSessionFileManager(session_name=session_name, workdir=workdir or env.PYLOGRAM_WORKDIR)
    else:
        raise TypeError(f"Account type {account_type} is not supported")
