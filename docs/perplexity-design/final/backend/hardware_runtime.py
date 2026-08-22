from __future__ import annotations
import asyncio
from hardware_executor import executor
from motion_backend import motion
from faults import fault_manager

async def hardware_loop() -> None:
    motion.set_executor(executor)
    while True:
        if fault_manager.e_stop:
            await asyncio.sleep(0.1)
            continue
        await asyncio.sleep(0.02)
