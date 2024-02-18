import asyncio
import logging
import time
import traceback
from typing import List, Optional, Union
from urllib.parse import urlparse

import aio_pika
import aiormq
from httpx import AsyncClient
from pydantic import BaseModel

from ..logger import logger
from ..stoppable import Stoppable
from .types import QueueRole, QueueTopicMessage


class RestAPI:
    def __init__(self, connection_url):
        p = urlparse(connection_url)
        # TODO: port should be configurable
        self.url = f"http://{p.username}:{p.password}@{p.hostname}:15672/api/"

        logging.getLogger("httpx").setLevel(
            logging.WARNING
        )  # disable verbose logging when global level is INFO

    async def get_queue(self, queue_name):
        async with AsyncClient() as client:
            r = await client.get(f"{self.url}queues/%2f/{queue_name}")
            q = r.json()
            # print(q)
            return q


class RabbitmqParams(BaseModel):
    exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.DIRECT
    routing_key: Union[str, List[str]] = ""
    prefetch_count: int = 1


class RabbitmqQueue(Stoppable):
    internal_queue: asyncio.Queue
    is_working: asyncio.Lock

    def __init__(
        self,
        role: QueueRole,
        connection_url: str,
        queue_name: Optional[str] = None,
        params: Optional[RabbitmqParams] = RabbitmqParams(),
    ):
        super().__init__()
        self.role = role
        self.url = connection_url
        self.params = params
        self.queue_name = queue_name  # rabbitmq router_key
        self.internal_queue = asyncio.Queue()
        self.ready_state = {
            self.role: asyncio.Event()
        }  # dict is for future: may support both server+client
        self.is_working = asyncio.Lock()
        self.rest_api = RestAPI(self.url)

    def run(self):
        # logger.info( f'{id(self.role)=} {id(QueueRole.Receiver)=} {id(QueueRole.Publisher)=}' )
        if self.role == QueueRole.Publisher:
            self.tasks.append(asyncio.create_task(self.publisher_loop()))
        elif self.role == QueueRole.Receiver:
            self.tasks.append(asyncio.create_task(self.receiver_loop()))
        else:
            raise Exception(f"BUG: unimplemented role {self.role}")
        super().run()

    async def stop(self):
        # logger.info( f'rabbitmq {self.internal_queue.qsize()=}')
        if self.internal_queue.qsize() > 0:
            await self.internal_queue.join()
            # logger.info( 'rabbitmq joined internal queue')
        await super().stop()
        # logger.info( 'rabbitmq super stopped')

    async def push(self, data):
        # logger.info(f'rabbitmq {self.queue_name} push')
        await self.internal_queue.put(data)
        # logger.info(f'rabbitmq {self.queue_name} pushed')

    async def pop(self, timeout=None):
        if timeout is None:
            # logger.info(f'rabbitmq pop {self.queue_name} no timeout')
            res = await self.internal_queue.get()
            # logger.info(f'rabbitmq {self.queue_name} poped {res}')
            return res
        try:
            async with asyncio.timeout(timeout):
                # logger.info(f'rabbitmq pop {self.queue_name} {timeout=}')
                res = await self.internal_queue.get()
                # logger.info(f'rabbitmq {self.queue_name} poped {res}')
                return res
        except TimeoutError:
            return None

    async def until_empty(self):
        last_log = 0
        while True:
            # is internal queue empty?
            if self.internal_queue.empty():
                # if receiver then is receiver queue empty?
                if self.role == QueueRole.Receiver:
                    queue = await self.rest_api.get_queue(self.queue_name)
                    if 'message_stats' in queue:
                        if time.time() - last_log > 5:
                            last_log = time.time()
                            logger.info(
                                f'=================== receiver queue size {self.queue_name} {self.params} {queue["messages"]=} {queue["messages_unacknowledged"]=} {queue["message_stats"]["publish"]=} {queue["message_stats"]["deliver_get"]=}'
                            )
                        if (
                            queue["messages"] == 0
                            and queue["messages_unacknowledged"] == 0
                            # ensures that at least anything was put into and got out of the queue.
                            and queue['message_stats']['publish'] > 0
                            and queue['message_stats']['deliver_get'] >= queue['message_stats']['publish']
                        ):
                            break
                    elif queue['messages'] == 0 and 'message_stats' not in queue:
                        # non touched queue => nothing to wait
                        break
                elif self.role == QueueRole.Publisher:
                    break
                else:
                    raise Exception("not implemented")
            await asyncio.sleep(1)

    async def mark_done(self, message: aio_pika.IncomingMessage):
        try:
            await message.ack()
        except aio_pika.exceptions.ChannelInvalidStateError:
            logger.error(
                f"ack for {message.message_id=} failed with ChannelInvalidStateError"
            )

    async def reject(self, message: aio_pika.IncomingMessage, requeue: bool):
        try:
            await message.reject(requeue)
        except aio_pika.exceptions.ChannelInvalidStateError:
            logger.error(
                f"reject for {message.message_id=} failed with ChannelInvalidStateError"
            )

    async def is_ready(self):
        await self.ready_state[self.role].wait()

    async def publisher_loop(self):
        try:
            while not await self.is_stopped():
                try:
                    connection = await aio_pika.connect_robust(self.url)
                except aiormq.exceptions.AMQPConnectionError:
                    logger.info("Failed connect to rabbitmq, waiting..")
                    await asyncio.sleep(5)  # TODO
                    continue

                logger.info(f"rabbitmq {connection=} --------------------")

                async with connection:
                    channel = await connection.channel()
                    logger.info(f"rabbitmq {channel=} ----------------------")

                    # Declaring queue
                    self.receiver_queue = await channel.declare_queue(
                        self.queue_name, durable=True
                    )

                    # TODO: can combine those conditions into single declare_exchange() expression
                    if (
                        self.params.exchange_type
                        == aio_pika.ExchangeType.DIRECT
                    ):
                        exchange = channel.default_exchange
                    elif (
                        self.params.exchange_type
                        == aio_pika.ExchangeType.TOPIC
                    ):
                        exchange = await channel.declare_exchange(
                            name=self._gen_queue_exchange_name(),
                            type=self.params.exchange_type,
                        )
                    else:
                        raise Exception(
                            f"not supported {self.params.exchange_type=}"
                        )

                    self.ready_state[QueueRole.Publisher].set()

                    try:
                        while not await self.is_stopped():
                            # logger.info( f'puslisher {self.queue_name} loop iteration')
                            message = await self.pop(1)
                            # logger.info( f'publisher loop {self.queue_name} poped {message=}')
                            if message is not None:
                                # logger.info( f'-------------------publishing msg {message.encode()}')

                                if type(message) is QueueTopicMessage:
                                    routing_key = ".".join(message.topic)
                                else:
                                    routing_key = self.queue_name

                                # logger.info( f'publishing into {routing_key=}')
                                await exchange.publish(
                                    aio_pika.Message(
                                        body=message.encode(),
                                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                    ),
                                    routing_key=routing_key,
                                )
                                # logger.info( f'published into {routing_key=}')

                                self.internal_queue.task_done()

                    except Exception as e:
                        logger.error(
                            f"!!!!!!!!!!!!!!!!!! exception in RabbitmqQueue::publisher_loop"
                        )
                        logger.error(traceback.format_exc())

                self.ready_state[QueueRole.Publisher].clear()

        except Exception as e:
            logger.error(f"!!!!!!!!!!!!!!!!!! exception in rabbitmq")
            logger.error(traceback.format_exc())

    def _gen_queue_exchange_name(self):
        return f"{self.queue_name}_exchange"

    async def receive_message(
        self, message: aio_pika.message.IncomingMessage
    ) -> None:
        # logger.info(
        #     f"RABBITMQ incoming message {type(message)} {message.message_id=} {message.info()=}"
        # )
        # logger.info(f"{message.channel=}")
        # logger.info(message.body)
        await self.push(message)

    async def receiver_loop(self):
        try:
            while not await self.is_stopped():
                try:
                    connection = await aio_pika.connect_robust(self.url)
                except aiormq.exceptions.AMQPConnectionError:
                    logger.info("Failed connect to rabbitmq, waiting..")
                    await asyncio.sleep(5)
                    continue

                logger.info(
                    f"rabbitmq {self.queue_name} {connection=} -----------------------"
                )

                try:
                    # Creating channel
                    channel = await connection.channel()
                    logger.info(
                        f"rabbitmq {self.queue_name} {channel=} ----------------------"
                    )

                    # Maximum message count which will be processing at the same time.
                    await channel.set_qos(
                        prefetch_count=self.params.prefetch_count
                    )

                    # Declaring queue
                    self.receiver_queue = await channel.declare_queue(
                        self.queue_name, durable=True
                    )

                    # print(self.receiver_queue)
                    if (
                        self.params.exchange_type
                        == aio_pika.ExchangeType.TOPIC
                    ):
                        exchange_name = self._gen_queue_exchange_name()
                        await channel.declare_exchange(
                            name=exchange_name,
                            type=aio_pika.ExchangeType.TOPIC,
                        )
                        rks = self.params.routing_key if isinstance(self.params.routing_key, list) else [
                            self.params.routing_key]
                        for rk in rks:
                            await self.receiver_queue.bind(
                                exchange_name, routing_key=rk
                            )
                    self.ready_state[QueueRole.Receiver].set()

                    logger.info(
                        f"rabbitmq {self.queue_name} consume start----------------------------"
                    )

                    await self.receiver_queue.consume(self.receive_message)
                    await self.stop_event.wait()

                    logger.info(
                        f"rabbitmq {self.queue_name} consume done----------------------------"
                    )

                except Exception as e:
                    logger.error(
                        f"!!!!!!!!!!!!!!!!!! exception in rabbitmq receiver_loop {e}"
                    )
                    logger.error(traceback.format_exc())

                self.ready_state[QueueRole.Receiver].clear()
        except Exception as e:
            logger.error(f"!!!!!!!!!!!!!!!!!! exception in rabbitmq {e}")
            logger.error(traceback.format_exc())
