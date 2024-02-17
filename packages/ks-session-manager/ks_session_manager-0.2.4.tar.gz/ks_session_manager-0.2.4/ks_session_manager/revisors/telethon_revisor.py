import asyncio
import logging
import pathlib
from pathlib import Path

import pydantic
import pydash
import telethon
import telethon.client
import telethon.helpers
import telethon.sessions

from ks_session_manager.clients import TelethonClient
from ks_session_manager.errors import SigningInDisabledError
from ks_session_manager.types import SessionMetadata
from ks_session_manager.types import SessionProxy
from ks_session_manager.utils import smartproxy

logger = logging.getLogger(__name__)


class TelethonRevizor:
    def __init__(self, threads: int = 1, *, dry_run: bool = False):
        self.threads = threads
        self.semaphore = asyncio.BoundedSemaphore(threads)
        self.logger = logging.getLogger(__name__)
        self.dry_run = dry_run

    async def revise_session_in_path(self, session_path: str | Path, proxy: SessionProxy | None = None):
        """
        Revise the session located at the given path.

        Parameters:
        - session_path: A string or Path object representing the path to the session file.
        - proxy: A SessionProxy object representing the proxy to be used. (default: None)

        Raises:
        - FileNotFoundError: If the provided path is not a file.
        - ValueError: If the provided path does not have a .session extension.
        - RuntimeError: If the metadata file is invalid.

        Returns: None
        """
        session_path = Path(session_path).resolve()

        async with self.semaphore:
            metadata_file = session_path.with_suffix(".json")

            if not session_path.is_file() or not metadata_file.is_file():
                raise FileNotFoundError("Provided path must be a file")

            if session_path.suffix != ".session":
                raise ValueError("Provided path must be a .session file")

            try:
                metadata = SessionMetadata.model_validate_json(metadata_file.read_text())
            except pydantic.ValidationError as e:
                raise RuntimeError(f"Invalid metadata file: {e}")

            if not bool(proxy):
                proxy = await smartproxy.get_proxy_by_phone_number(metadata.phone_number, rotating=True)
                self.logger.info("Using proxy: %s", proxy.link)

            self.logger.info(f"Session revision started for session {session_path.stem}")
            telethon_client = TelethonClient(session_path, metadata, proxy=proxy)
            dir_to_move: pathlib.Path | None = None

            if not self.dry_run:
                try:
                    # noinspection PyUnresolvedReferences
                    await telethon_client.start(
                        phone=lambda: session_path.stem,
                        password=lambda: metadata.two_factor_password,
                    )
                except telethon.errors.PhoneNumberInvalidError:
                    self.logger.error(f"Session {session_path.stem} phone number invalid")
                    dir_to_move = session_path.parent / "phone_number_invalid"
                except telethon.errors.PhoneNumberBannedError:
                    self.logger.error(f"Session {session_path.stem} phone number banned")
                    dir_to_move = session_path.parent / "phone_number_banned"
                except telethon.errors.UnauthorizedError as e:
                    self.logger.error(f"Session {session_path.stem} unauthorized: {e}")
                    dir_to_move = session_path.parent / pydash.snake_case(e.__class__.__name__.replace('_error', ''))
                except telethon.errors.AuthKeyError as e:
                    self.logger.error(f"Session {session_path.stem} auth key error")
                    dir_to_move = session_path.parent / pydash.snake_case(e.__class__.__name__.replace('_error', ''))
                except SigningInDisabledError as e:
                    self.logger.error(f"Session {session_path.stem} is not signed in: {e.code_type}")
                    dir_to_move = session_path.parent / "not_signed_in" / pydash.snake_case(e.code_type)
                except ConnectionError:
                    self.logger.error(f"Session {session_path.stem} connection error")
                    dir_to_move = session_path.parent / "connection_error"
                except Exception as e:
                    self.logger.error(f"Session {session_path.stem} unhandled error: {e.__class__.__name__}: {e}")
                    dir_to_move = None
                else:
                    self.logger.info(f"Session {session_path.stem} is alive")
                    self.logger.info(f"Authorized as {telethon_client.me.id}: {telethon_client.me.phone}")
                    dir_to_move = session_path.parent / "alive"
                finally:
                    await telethon_client.disconnect()

            if dir_to_move:
                dir_to_move.mkdir(parents=True, exist_ok=True)
                session_path.rename(dir_to_move / session_path.name)
                metadata_file.rename(dir_to_move / metadata_file.name)

            self.logger.info(f"Session revision finished for session {session_path.stem}")

    async def revise_all_in_path(self, path: str | Path, *, limit: int | None = None):
        """
        Revise All in Path

        Revise all session files in a given directory path.

        Parameters:
        - path: str | Path - The directory path containing the session files to be revised.
        - limit: int | None - Optional. The maximum number of session files to be revised. Default is None, which means to revise all session files in the directory.

        Raises:
        - NotADirectoryError: If the provided path is not a directory.

        Example usage:
        ```python
        await revise_all_in_path('/path/to/directory', limit=5)
        ```
        """
        path = Path(path).resolve()

        if not path.is_dir():
            raise NotADirectoryError("Provided path must be a directory")

        session_files = [
            file
            for file in path.iterdir()
            if file.is_file() and file.suffix == ".session"
        ]

        if limit:
            session_files = session_files[:limit]

        tasks = [self.revise_session_in_path(file) for file in session_files]

        self.logger.info(
            f"Starting {len(tasks)} revisions. "
            f"Simultaneous count: {self.threads}"
        )
        await asyncio.gather(*tasks)
        self.logger.info("All revisions finished")
