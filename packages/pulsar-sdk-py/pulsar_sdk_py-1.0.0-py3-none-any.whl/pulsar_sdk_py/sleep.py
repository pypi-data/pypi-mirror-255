import asyncio

from typing import Callable


class ConditionFailed(Exception):
    pass


async def wait_for_condition(condition_check: Callable, timeout: int, raise_on_condition: Callable | None = None):
    async def check():
        while True:
            if condition_check():
                return
            if raise_on_condition and raise_on_condition():
                raise ConditionFailed
            await asyncio.sleep(0.1)  # Wait for 100ms

    await asyncio.wait_for(check(), timeout)
