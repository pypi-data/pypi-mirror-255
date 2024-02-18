from enum import Enum
from abc import abstractmethod
import json
from typing import Any, List, Optional, Set, Union, NamedTuple, TypeAlias

from pydantic import BaseModel, BaseSettings, AnyUrl, validator
from .storage import FileStorage
from .session_manager import Session
# from pydantic_settings import BaseSettings

QUEUE_WORKER_TASKS = "worker_tasks"
QUEUE_REPORTS = "worker_reports"
QUEUE_EVAL_TASKS = "eval_tasks"
QUEUE_TOPICS = "topics"

DEFAULT_RABBITMQ_HOST = "rabbitmq.crawler"
DEFAULT_RABBITMQ_PORT: int = 5672
DEFAULT_REDIS_HOST = "redis.crawler"
DEFAULT_REDIS_PORT: int = 6379

DEFAULT_CONNECTION_URL: str = "amqp://guest:guest@{host}:{port}/".format(
    host=DEFAULT_RABBITMQ_HOST,
    port=DEFAULT_RABBITMQ_PORT)

DEFAULT_BACKEND_API_URL: str = "https://openlicense.ai/openlicense/api/"
DEFAULT_BACKEND_HINTS_PERIOD: int = 10  # seconds


class InvalidUsageException(Exception):
    pass


class BaseCrawlerSettings(BaseSettings):
    def fload(self, json_path):
        """fills self using json file path"""
        with open(json_path, 'r') as fp:
            config = json.load(fp)  # expects dict output
            self.load(config)

    @abstractmethod
    def load(self, config: dict):
        pass


class SchedulerSettings(BaseCrawlerSettings):
    QUEUE_CONNECTION_URL: str = DEFAULT_CONNECTION_URL
    BACKEND_API_URL: str = DEFAULT_BACKEND_API_URL
    BACKEND_HINTS_PERIOD: int = DEFAULT_BACKEND_HINTS_PERIOD

    REDIS_HOST: str = DEFAULT_REDIS_HOST
    REDIS_PORT: int = DEFAULT_REDIS_PORT
    # cli settings
    CLI_MODE: bool = False

    def load(self, config: dict):
        """fills self with json config"""
        # Queue
        queue = config.get('queue', {})
        queue_connection_url = queue.get('connection_url')
        if queue_connection_url is not None:
            self.QUEUE_CONNECTION_URL = queue_connection_url

        backend = config.get('backend', {})
        api_url = backend.get('api_url')
        if api_url is not None:
            self.BACKEND_API_URL = api_url
        hints_period = backend.get('hints_period')
        if hints_period is not None:
            self.BACKEND_HINTS_PERIOD = hints_period

        redis = config.get('redis', {})
        redis_host = redis.get('host')
        if redis_host is not None:
            self.REDIS_HOST = redis_host
        redis_port = redis.get('port')
        if redis_port is not None:
            self.REDIS_PORT = redis_port


class WorkerSettings(BaseCrawlerSettings):
    QUEUE_CONNECTION_URL: str = DEFAULT_CONNECTION_URL
    TODO_QUEUE_SIZE: int = 1

    ATTEMPTS_PER_URL: int = 3
    ATTEMPTS_DELAY: int = 5  # seconds
    STORAGE_PATH: str = "/storage/"

    REDIS_HOST: str = DEFAULT_REDIS_HOST
    REDIS_PORT: int = DEFAULT_REDIS_PORT

    # None: access is configured on AWS, bucket is NOT PUBLIC
    # "": bucket is PUBLIC
    # S3_IMAGESHACK_ACCESS_KEY: Optional[str] = None
    # S3_IMAGESHACK_ACCESS_SECRET: Optional[str] = None

    # GOOGLE_DRIVE_API_KEY: str = ""

    CLI_MODE: bool = False

    USE_ONLY_PLUGINS: Optional[List[str]] = None
    ADDITIONAL_PLUGINS: Optional[List[str]] = None

    plugins_config: dict = {}

    def load(self, config: dict):
        """fills self with json config"""
        # Queue
        queue = config.get('queue', {})
        queue_connection_url = queue.get('connection_url')
        if queue_connection_url is not None:
            self.QUEUE_CONNECTION_URL = queue_connection_url
        queue_size_limit = queue.get('size_limit')
        if queue_size_limit is not None:
            self.TODO_QUEUE_SIZE = queue_size_limit

        # redis
        redis = config.get('redis', {})
        redis_host = redis.get('host')
        if redis_host is not None:
            self.REDIS_HOST = redis_host
        redis_port = redis.get('port')
        if redis_port is not None:
            self.REDIS_PORT = redis_port

        # Storage
        storage = config.get('storage', {})
        worker_storage = storage.get('worker', {})
        storage_path = worker_storage.get('path')
        if storage_path is not None:
            self.STORAGE_PATH = storage_path

        # plugins
        self.plugins_config = config.get('plugins', {})


class BaseProducerSettings(BaseCrawlerSettings):
    QUEUE_CONNECTION_URL: str = DEFAULT_CONNECTION_URL
    BACKEND_API_URL: str = DEFAULT_BACKEND_API_URL
    STORAGE_PATH: Optional[str] = None
    WORKER_STORAGE_PATH: str = "/worker_storage/"

    REDIS_HOST: str = DEFAULT_REDIS_HOST
    REDIS_PORT: int = DEFAULT_REDIS_PORT

    CLI_MODE: bool = False

    def load(self, config: dict):
        """fills self with json config"""
        backend = config.get('backend', {})
        api_url = backend.get('api_url')
        if api_url is not None:
            self.BACKEND_API_URL = api_url
        
        # Queue
        queue = config.get('queue', {})
        queue_connection_url = queue.get('connection_url')
        if queue_connection_url is not None:
            self.QUEUE_CONNECTION_URL = queue_connection_url

        # redis
        redis = config.get('redis', {})
        redis_host = redis.get('host')
        if redis_host is not None:
            self.REDIS_HOST = redis_host
        redis_port = redis.get('port')
        if redis_port is not None:
            self.REDIS_PORT = redis_port

        # Storage
        storage = config.get('storage', {})
        worker_storage = storage.get('worker', {})
        storage_path = worker_storage.get('path')
        if storage_path is not None:
            self.WORKER_STORAGE_PATH = storage_path
        producer_storage = storage.get('producer', {})
        storage_path = producer_storage.get('path')
        if storage_path is not None:
            self.STORAGE_PATH = storage_path


class CrawlerHintURLStatus(Enum):
    Unprocessed = 0
    Success = 1
    Failure = 2
    Processing = 3
    Rejected = 4
    Canceled = 5


class DatapoolContentType(Enum):
    Text = "Text"
    Image = "Image"
    Video = "Video"
    Audio = "Audio"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        if self.value == DatapoolContentType.Text:
            return 1
        if self.value == DatapoolContentType.Image:
            return 2
        if self.value == DatapoolContentType.Video:
            return 3
        if self.value == DatapoolContentType.Audio:
            return 4
        raise Exception(
            f"Not supported DatapoolContentType __hash__ {self.value}"
        )


class BaseCrawlerResult(BaseModel):
    pass


class CrawlerContent(BaseCrawlerResult):
    tag_id: Optional[str] = None
    copyright_tag_id: Optional[str] = None
    platform_tag_id: Optional[str] = None
    type: DatapoolContentType
    storage_id: Any
    url: str

    def to_dict(self):
        res = self.__dict__
        res["type"] = res["type"].value
        return res


class CrawlerBackTask(BaseCrawlerResult):
    url: str

    def to_dict(self):
        res = self.__dict__
        return res


class CrawlerNop(BaseCrawlerResult):
    pass

PriorityTimestamp : TypeAlias = int
class Evaluation(BaseModel):
    nsfw: bool
    score: float
    weight: float
    embeddings: Optional[List[float]]
    priority_timestamp: Optional[PriorityTimestamp]

class WorkerContext(NamedTuple):
    session: Session
    storage: FileStorage


class WorkerTask(NamedTuple):
    url: AnyUrl
    content_type: Optional[DatapoolContentType]
