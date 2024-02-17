from dataclasses import dataclass
import asyncio

from zaber_motion import wait_all


@dataclass
class Shared:
    value = 0

async def coroutine(shared: Shared, count):
    await asyncio.sleep(0)
    shared.value += count
    return count

def test_runs_multiple_coroutines():
    shared = Shared()
    coros = [coroutine(shared, i) for i in range(1, 5)]
    result = wait_all(*coros)
    assert result == [1, 2, 3, 4]
    assert shared.value == 10
