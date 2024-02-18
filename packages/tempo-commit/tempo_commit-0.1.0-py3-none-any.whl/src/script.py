import asyncio

import aiofiles

from config import get_settings
from services.commits import commit_and_add_worklog

settings = get_settings()


async def get_commit_message():
    async with aiofiles.open(".git/COMMIT_EDITMSG", "r") as file:
        commit_message = await file.read()
    return commit_message.strip()


async def pre_commit():
    commit_message = await get_commit_message()
    await commit_and_add_worklog(message=commit_message)


if __name__ == "__main__":
    asyncio.run(pre_commit())
