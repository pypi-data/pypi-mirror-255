# Session converter from Telethon session + json to Pyrogram and vice versa

## Examples

### From telethon to pylogram

```python
import asyncio
import logging

from ks_session_manager.converter import Converter

API_ID = 123456
API_HASH = ""
PHONE_NUMBER = ""


async def main():
    converter = await Converter.from_telethon(PHONE_NUMBER, workdir="./telethon_sessions_path")

    try:
        await converter.export_pylogram_session()
    except FileExistsError as e:
        # Already exported
        logging.warning(e)

    client = await converter.get_pylogram_client()

    async with client:
        me = await client.get_me()
        print(me)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

```

### Telethon sessions revision

```python
import asyncio
import logging

from ks_session_manager.revisors import TelethonRevizor


async def main():
    revizor = TelethonRevizor(
        threads=20,  # How many revisions to run simultaneously
        dry_run=False  # If True, revisions will not actually connect to Telegram, only logs will be printed
    )
    await revizor.revise_all_in_path("./telethon_sessions_path", limit=20)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

```