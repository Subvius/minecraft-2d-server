import asyncio


async def run_multiple_tasks(tasks: list):
    await asyncio.gather(*tasks)
