from urllib.parse import urlparse

# from pydantic import AnyUrl, BaseModel
from ..logger import logger
from .types import *


class GenericQueue:
    def __init__(
        self, role: QueueRole, url=None, name=None, size=1, topic=None
    ):
        parsed = urlparse(url)
        if parsed.scheme == "amqp":
            import aio_pika

            from .rabbitmq import RabbitmqParams, RabbitmqQueue

            params = RabbitmqParams(prefetch_count=size)
            if topic is not None:
                params.exchange_type = aio_pika.ExchangeType.TOPIC
                params.routing_key = topic

            logger.info(
                f"RabbitmqQueue {url=}"
            )
            self.queue = RabbitmqQueue(role, url, name, params)
        else:
            raise Exception(f"not supported {url=}")

    def run(self):
        self.queue.run()

    async def stop(self):
        await self.queue.stop()

    async def until_empty(self):
        await self.queue.until_empty()

    async def push(self, data):
        await self.queue.push(data)

    async def pop(self, timeout=None):
        return await self.queue.pop(timeout)

    async def reject(self, message, requeue=True):
        await self.queue.reject(message, requeue)

    async def mark_done(self, message):
        await self.queue.mark_done(message)
