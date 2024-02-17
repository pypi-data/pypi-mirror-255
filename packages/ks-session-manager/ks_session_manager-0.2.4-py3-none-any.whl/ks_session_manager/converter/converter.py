from __future__ import annotations

import logging
import pathlib

import pylogram.session

from ks_session_manager.clients import PylogramClient
from ks_session_manager.clients import TelethonClient
from ks_session_manager.env import env
from ks_session_manager.managers import BaseSessionFileManager
from ks_session_manager.managers import create_session_manager_of_type
from ks_session_manager.types import AccountType
from ks_session_manager.types import SessionData
from ks_session_manager.types import SessionMetadata
from ks_session_manager.types import SessionProxy
from ks_session_manager.types import TelegramPlatform
from ks_session_manager.utils.metadata_generator import MetadataGenerator


class Converter:
    def __init__(
            self,
            *,
            session_metadata: SessionMetadata | None = None,
            session_data: SessionData | None = None,
            proxy: SessionProxy | None = None
    ):
        self.session_data = session_data
        self.session_metadata = session_metadata
        self.proxy = proxy
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @classmethod
    async def create(
            cls,
            account_type: AccountType,
            session_name: str,
            *,
            workdir: str | pathlib.Path | None = None,
            proxy: SessionProxy | None = None,
            generate_metadata_if_not_exists: bool = False,
            generate_metadata_platform: TelegramPlatform = TelegramPlatform.DESKTOP_LINUX,
            online: bool = False
    ) -> Converter:
        """
        Create a converter object for the specified account type and session name.

        Parameters:
            account_type (AccountType): The type of the account.
            session_name (str): The name of the session.
            workdir (str | pathlib.Path | None, optional): The working directory for the session. Defaults to None.
            proxy (SessionProxy | None, optional): The session proxy. Defaults to None.
            generate_metadata_if_not_exists (bool, optional): Whether to generate session metadata if it doesn't exist. Defaults to False.
            generate_metadata_platform (TelegramPlatform, optional): The platform for generating metadata. Defaults to TelegramPlatform.DESKTOP_LINUX.
            online (bool, optional): Whether to be in online mode. Defaults to False.

        Returns:
            Converter: The created converter object.

        Raises:
            NotImplementedError: If online mode is enabled.

        """
        manager: BaseSessionFileManager = create_session_manager_of_type(account_type, session_name, workdir=workdir)
        session_data = await manager.read_session_storage()

        try:
            session_metadata = await manager.read_session_metadata()
        except FileNotFoundError:
            if online:
                raise NotImplementedError("Online mode is not implemented yet")
            elif generate_metadata_if_not_exists:
                session_metadata = MetadataGenerator(generate_metadata_platform, session_name).generate()
            else:
                raise

        return cls(session_metadata=session_metadata, session_data=session_data, proxy=proxy)

    @classmethod
    async def from_telethon(
            cls,
            session_name: str,
            *,
            workdir: str | pathlib.Path | None = env.TELETHON_WORKDIR,
            proxy: SessionProxy | None = None,
            generate_metadata_if_not_exists: bool = False,
            generate_metadata_platform: TelegramPlatform = TelegramPlatform.DESKTOP_LINUX,
            online: bool = False
    ) -> Converter:
        """

        Converts a Telethon session into a Converter instance.

        Parameters:
            session_name (str): The name of the Telethon session to convert.
            workdir (str | pathlib.Path | None, optional): The directory where the converted session file will be stored. Defaults to env.TELETHON_WORKDIR.
            proxy (SessionProxy | None, optional): The proxy to be used for the converted session. Defaults to None.
            generate_metadata_if_not_exists (bool, optional): Whether to generate metadata for the converted session if it doesn't exist. Defaults to False.
            generate_metadata_platform (TelegramPlatform, optional): The platform to be used for generating metadata for the converted session. Defaults to TelegramPlatform.DESKTOP_LINUX.
            online (bool, optional): Whether the converted session should be used in online mode. Defaults to False.

        Returns:
            Converter: The Converter instance created from the Telethon session.

        """
        return await cls.create(
            account_type=AccountType.TELETHON,
            session_name=session_name,
            workdir=workdir,
            proxy=proxy,
            generate_metadata_if_not_exists=generate_metadata_if_not_exists,
            generate_metadata_platform=generate_metadata_platform,
            online=online
        )

    @classmethod
    async def from_pylogram(
            cls,
            session_name: str,
            *,
            workdir: str | pathlib.Path | None = env.PYLOGRAM_WORKDIR,
            proxy: SessionProxy | None = None,
            generate_metadata_if_not_exists: bool = False,
            generate_metadata_platform: TelegramPlatform = TelegramPlatform.DESKTOP_LINUX,
            online: bool = False
    ) -> Converter:
        """

        Converts a Pyrogram session into a Converter instance.

        Parameters:
            session_name (str): The name of the Pyrogram session.
            workdir (str | pathlib.Path | None): The directory path where session files will be stored. Defaults to env.PYLOGRAM_WORKDIR.
            proxy (SessionProxy | None): The session proxy to be used. Defaults to None.
            generate_metadata_if_not_exists (bool): Whether to generate session metadata if it doesn't exist. Defaults to False.
            generate_metadata_platform (TelegramPlatform): The platform used to generate session metadata. Defaults to TelegramPlatform.DESKTOP_LINUX.
            online (bool): Whether to create an online session. Defaults to False.

        Returns:
            Converter: An instance of the Converter class.

        """
        return await cls.create(
            account_type=AccountType.PYLOGRAM,
            session_name=session_name,
            workdir=workdir,
            proxy=proxy,
            generate_metadata_if_not_exists=generate_metadata_if_not_exists,
            generate_metadata_platform=generate_metadata_platform,
            online=online
        )

    async def export_session(
            self,
            account_type: AccountType,
            session_name: str | None = None,
            workdir: str | pathlib.Path | None = None,
            export_metadata: bool = True
    ):
        """

        Export a session to the specified account type, session name, and working directory.

        :param account_type: The account type to export the session to.
        :type account_type: AccountType
        :param session_name: The name of the session to be exported. If not provided, it defaults to the phone number associated with the current session.
        :type session_name: str, optional
        :param workdir: The working directory where the session should be exported. If not provided, it defaults to the current working directory.
        :type workdir: str or pathlib.Path, optional
        :param export_metadata: Indicates whether to export the session metadata alongside the session data. Defaults to True.
        :type export_metadata: bool, optional
        """
        if not bool(session_name):
            session_name = self.session_metadata.phone_number

        manager = create_session_manager_of_type(account_type, session_name, workdir=workdir)
        await manager.write_session_storage(self.session_data)
        self.logger.info(f"Session successfully exported to {manager.session_path}")

        if export_metadata:
            await manager.write_session_metadata(self.session_metadata)
            self.logger.info(f"Session metadata successfully exported to {manager.session_json_metadata_path}")

    async def export_telethon_session(
            self,
            session_name: str = None,
            workdir: str | pathlib.Path = env.TELETHON_WORKDIR,
            export_metadata: bool = True
    ):
        """
        Exports the Telethon session to a specified file or directory.

        :param session_name: Optional name of the session file. If not provided, a default name will be used.
        :type session_name: str, optional
        :param workdir: Optional working directory where the session file will be exported. If not provided, the default work directory will be used.
        :type workdir: str or pathlib.Path, optional
        :param export_metadata: Optional flag indicating whether to export the session metadata. Default is True.
        :type export_metadata: bool, optional
        :return: None
        :rtype: None
        """
        await self.export_session(AccountType.TELETHON, session_name, workdir, export_metadata)

    async def export_pylogram_session(
            self,
            session_name: str = None,
            workdir: str | pathlib.Path = env.PYLOGRAM_WORKDIR,
            export_metadata: bool = True
    ):
        """
        Export a Pylogram session to a specified file or directory.

        :param session_name: Optional name of the session file. If not provided, a default name will be used.
        :type session_name: str, optional
        :param workdir: Optional working directory where the session file will be exported. If not provided, the default work directory will be used.
        :type workdir: str or pathlib.Path, optional
        :param export_metadata: Optional flag indicating whether to export the session metadata. Default is True.
        :type export_metadata: bool, optional

        :return: None
        :rtype: None

        """
        await self.export_session(AccountType.PYLOGRAM, session_name, workdir, export_metadata)

    async def get_telethon_client(
            self,
            *,
            in_memory: bool = False,
            proxy: SessionProxy | None = None,
            workdir: str | pathlib.Path = env.TELETHON_WORKDIR,
    ) -> TelethonClient:
        """
        Asynchronously retrieves a TelethonClient instance with the specified parameters.

        Parameters:
        - in_memory (bool): Whether to store the session storage in memory. Defaults to False.
        - proxy (SessionProxy | None): The session proxy to use. Defaults to None.
        - workdir (str | pathlib.Path): The directory path for storing session data. Defaults to env.TELETHON_WORKDIR.

        Returns:
        - TelethonClient: The instantiated TelethonClient object.

        Example Usage:
        ```python
        client = await get_telethon_client(in_memory=True, proxy=my_proxy, workdir="/path/to/directory")
        ```
        """
        session_name = self.session_metadata.phone_number
        manager = create_session_manager_of_type(AccountType.TELETHON, session_name, workdir=workdir)
        session_storage = await manager.write_session_storage(self.session_data, in_memory=in_memory)

        if not bool(proxy):
            proxy = self.proxy

        return TelethonClient(self.session_metadata, session_storage=session_storage, proxy=proxy)

    # Pylogram
    async def get_pylogram_client(
            self,
            *,
            in_memory: bool = False,
            proxy: SessionProxy | None = None,
            workdir: str | pathlib.Path = env.PYLOGRAM_WORKDIR,
    ) -> PylogramClient:
        """

        Asynchronously creates and returns a PylogramClient object.

        Parameters:
        - `in_memory` : bool, optional (default=False)
            If True, the session storage will be stored in memory instead of on disk.

        - `proxy` : SessionProxy or None, optional (default=None)
            The proxy to be used for the PylogramClient object. If None, the proxy from the session metadata will be used.

        - `workdir` : str or pathlib.Path, optional (default=env.PYLOGRAM_WORKDIR)
            The directory path where the session storage will be stored.

        Returns:
        - `PylogramClient` : The PylogramClient object that is created.

        """
        session_name = self.session_metadata.phone_number
        manager = create_session_manager_of_type(AccountType.PYLOGRAM, session_name, workdir=workdir)
        session_storage = await manager.write_session_storage(self.session_data, in_memory=in_memory)

        if not bool(proxy):
            proxy = self.proxy

        return PylogramClient(self.session_metadata, session_storage=session_storage, proxy=proxy)

    async def get_pylogram_session_string(self) -> str:
        client = await self.get_pylogram_client(in_memory=True)
        storage: pylogram.storage.Storage = client.storage
        await storage.open()
        session_string = await storage.export_session_string()
        await storage.close()
        return session_string

    async def get_telethon_session_string(self) -> str:
        client = await self.get_telethon_client(in_memory=True)
        return await client.export_session_string()

    @property
    def self_user_id(self) -> int | None:
        return self.session_data.user_id or self.session_metadata.user_id
