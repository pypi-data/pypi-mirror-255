import asyncio

# import json
# import time
import traceback
from typing import Optional

from ..common.backend_api import BackendAPI
from ..common.logger import logger
from ..common.queues import (
    GenericQueue,
    QueueMessage,
    QueueMessageType,
    QueueRole,
)
from ..common.stoppable import Stoppable

# from .common.tasks_db import Hash
# from .common.tasks_db.redis import RedisTasksDB
from ..common.session_manager import SessionManager
from ..common.types import (
    DatapoolContentType,
    QUEUE_REPORTS,
    QUEUE_WORKER_TASKS,
    CrawlerHintURLStatus,
    SchedulerSettings,
    InvalidUsageException,
)

# import httpx


class CrawlerScheduler(Stoppable):
    # 1. task:
    #   - get hint urls from the backend, put into tasks_db, status is changed at the backend at once
    #   - check "processing" tasks: ping worker. If it's dead then task is moved back to the queue
    # 2. api: get urls from workers, put into tasks_db
    #   tips:
    #   - reject existing urls: request redis by url hash
    # 3. api: worker gets a new task(s?) from queue:
    #   tips:
    #   - tasks_db: (redis) task should be moved into a separate key as "in progress", worker ID/IP/etc should be remembered to be able to ping
    # 4. api: worker notifies about finished task
    #    - remove task from "processing"
    #    - if it's a backend hint url, then update its status by calling backend api

    cli_tasks: Optional[asyncio.Queue] = None

    def __init__(self, cfg: Optional[SchedulerSettings] = None):
        super().__init__()
        self.cfg = cfg if cfg is not None else SchedulerSettings()

        if self.cfg.CLI_MODE is True:
            self.cli_tasks = asyncio.Queue()
        else:
            self.api = BackendAPI(url=self.cfg.BACKEND_API_URL)

        self.session_manager = SessionManager(
            self.cfg.REDIS_HOST, self.cfg.REDIS_PORT)

        # self.tasks_db = RedisTasksDB(
        #     host=self.cfg.REDIS_HOST, port=self.cfg.REDIS_PORT
        # )
        self.todo_queue = GenericQueue(
            role=QueueRole.Publisher,
            url=self.cfg.QUEUE_CONNECTION_URL,
            name=QUEUE_WORKER_TASKS,
        )
        logger.info("created publisher worker_tasks")
        self.reports_queue = GenericQueue(
            role=QueueRole.Receiver,
            url=self.cfg.QUEUE_CONNECTION_URL,
            name=QUEUE_REPORTS,
        )
        logger.info("created receiver reports")

        if self.cfg.CLI_MODE:
            self.cli_session = self.session_manager.create()
            logger.info(f'created session {self.cli_session.id}')

            # TODO: this mechanism will not work for multiple workers/producers
            self.stop_task_processed = asyncio.Event()

    async def wait(self):
        """for CLI mode usage only"""
        if not self.cfg.CLI_MODE:
            logger.error('scheduler invalid usage')
            raise InvalidUsageException("not a cli mode")

        await self.stop_task_processed.wait()

        waiters = (
            self.todo_queue.until_empty(),
            self.reports_queue.until_empty(),
        )
        await asyncio.gather(*waiters)
        logger.info('scheduler wait done')

    def run(self):
        self.tasks.append(asyncio.create_task(self.hints_loop()))
        self.tasks.append(asyncio.create_task(self.reports_loop()))
        self.todo_queue.run()
        self.reports_queue.run()
        super().run()

    async def stop(self):
        logger.info("scheduler stopping")
        await self.todo_queue.stop()
        logger.info("todo_queue stopped")
        await self.reports_queue.stop()
        logger.info("reports_queue stopped")
        await super().stop()
        logger.info("super stopped")

    async def _set_task_status(self, session_id, data):
        # hash, status: CrawlerHintURLStatus, contents
        logger.info(f"set_task_status: {session_id=} {data=}")

        session = self.session_manager.get(session_id)

        meta = session.get_meta()
        logger.info(f'{meta=}')
        if not meta:
            return False

        status = CrawlerHintURLStatus(data["status"])

        if status in (
                CrawlerHintURLStatus.Success, CrawlerHintURLStatus.Failure,
                CrawlerHintURLStatus.Rejected):
            if status == CrawlerHintURLStatus.Success:
                session.inc_complete_urls()
            elif status == CrawlerHintURLStatus.Failure:
                session.inc_failed_urls()
            else:
                session.inc_rejected_urls()

            if (meta['total_tasks'] == meta['complete_tasks'] + meta['failed_tasks'] + meta['rejected_tasks'] + 1
                # and meta[ 'crawled_content'] == meta[ 'evaluated_content']      <--- this will not work here, because producer will evaluate later than task is complete
                    and meta['hint_id'] is not None):
                # this is hint url from server => have to update status on the backend
                if not self.cfg.CLI_MODE:
                    await self.api.set_hint_url_status(meta["hint_id"], status, session_id)

    async def _add_task(self, session_id, task: dict):
        if not self.session_manager.has(session_id):
            logger.error(f'Session not found: {session_id=}')
            return False

        session = self.session_manager.get(session_id)

        if 'url' in task:
            if not session.has_url(task['url']):
                session.add_url(task['url'])

                await self.todo_queue.push(
                    QueueMessage(session_id, QueueMessageType.Task, data=task)
                )
            else:
                logger.info('task exists, ignored')
                return False
        elif 'stop_running' in task:
            await self.todo_queue.push(
                QueueMessage(session_id, QueueMessageType.Stop)
            )
        else:
            raise Exception(f'unsupported {task=}')

        # logger.info( 'pushed')
        return True
        # return hash

    # return False

    async def add_download_task(self, url, content_type: Optional[DatapoolContentType] = None):
        """for cli mode: pushing url to the queue. Scheduler will run until empty string is added"""
        if self.cli_tasks is None:
            logger.error('scheduler invalid usage')
            raise InvalidUsageException("not a cli mode")
        await self.cli_tasks.put((url, content_type))

    async def _get_hints(self):
        hints = None
        if not self.cfg.CLI_MODE:
            # deployment mode
            try:
                hints = await self.api.get_hint_urls(limit=10)
                for hint in hints:
                    session = self.session_manager.create(
                        hint_id=hint.get('id', 0),
                        url=hint.get('url', '')
                    )
                    hint['session_id'] = session.id

            except Exception as e:
                logger.error(f"Failed get hints: {e}")
        else:
            # cli mode
            try:
                (url, content_type) = await asyncio.wait_for(self.cli_tasks.get(), timeout=1)
                if len(url) > 0:
                    hints = [{"url": url, "content_type": content_type,
                              "session_id": self.cli_session.id}]
                else:
                    hints = [{'stop_running': True,
                              "session_id": self.cli_session.id}]
            except asyncio.TimeoutError:
                pass
        return hints

    async def hints_loop(self):
        # infinitely fetching URL hints by calling backend api
        try:
            while not await self.is_stopped():
                if self.session_manager.is_ready():
                    hints = await self._get_hints()
                    if hints is not None:
                        for hint in hints:
                            logger.info(f"got hint: {hint}")

                            if await self._add_task(
                                hint.get('session_id'),
                                hint
                            ):
                                if "id" in hint:
                                    await self.api.set_hint_url_status(
                                        hint["id"],
                                        CrawlerHintURLStatus.Processing,
                                        hint['session_id']
                                    )
                            else:
                                logger.error('failed add task, REJECTING')
                                if "id" in hint:
                                    await self.api.set_hint_url_status(
                                        hint["id"],
                                        CrawlerHintURLStatus.Rejected,
                                    )
                                    self.session_manager.remove(
                                        hint['session_id'])

                    if not self.cfg.CLI_MODE:
                        await asyncio.sleep(self.cfg.BACKEND_HINTS_PERIOD)
                else:
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(
                f"!!!!!!! Exception in CrawlerScheduler::hints_loop() {e}"
            )
            logger.error(traceback.format_exc())

    async def reports_loop(self):
        # receive reports from workers
        try:
            while not await self.is_stopped():
                message = await self.reports_queue.pop(timeout=1)
                if message:
                    try:
                        qm = QueueMessage.decode(message.body)
                        if qm.type == QueueMessageType.Task:
                            # logger.info("new task from worker")
                            # logger.info(f"{qm=}")
                            await self._add_task(qm.session_id, qm.data)
                        elif qm.type == QueueMessageType.Report:
                            await self._set_task_status(qm.session_id, qm.data)
                        elif qm.type == QueueMessageType.Stop:
                            logger.info('scheduler: got stop from worker')
                            self.stop_task_processed.set()
                        else:
                            logger.error(f"Unsupported QueueMessage {qm=}")

                    except Exception as e:
                        logger.error(f"Failed decode process report")
                        logger.error(traceback.format_exc())

                    await self.reports_queue.mark_done(message)

        except Exception as e:
            logger.error(
                f"!!!!!!! Exception in CrawlerScheduler::reports_loop() {e}"
            )
            logger.error(traceback.format_exc())
