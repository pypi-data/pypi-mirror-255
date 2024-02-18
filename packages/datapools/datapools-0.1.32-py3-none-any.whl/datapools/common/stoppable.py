import asyncio


class StoppableException(Exception):
    pass


class Stoppable:
    def __init__(self):
        self.stop_event = asyncio.Event()
        self.tasks = []
        self.is_running = False

    def run(self):
        if len(self.tasks) == 0:
            raise StoppableException("call me after child's run()")
        self.is_running = True

    async def stop(self):
        if not self.is_running:
            raise StoppableException("stop() before run()")

        self.stop_event.set()
        await asyncio.wait(self.tasks, return_when=asyncio.ALL_COMPLETED)

    async def is_stopped(self, timeout=0):
        if timeout == 0:
            return self.stop_event.is_set()

        try:
            async with asyncio.timeout(timeout):
                await self.stop_event.wait()
            return True
        except TimeoutError:
            pass
        return False
