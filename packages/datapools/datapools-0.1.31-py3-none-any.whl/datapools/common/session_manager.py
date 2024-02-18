import json
import time
from hashlib import md5
from typing import Literal, Union
from .logger import logger

import redis

# from ..logger import logger

SESSION_METADATA_KEY_PREFIX = 'crawler_session_meta_'  # hash
SESSION_URLS_KEY_PREFIX = 'crawler_session_urls_'  # set
SESSION_CONTENT_KEY_PREFIX = 'crawler_session_content_'  # set


class Session:
    id: str

    def __init__(self, session_id, redis_inst):
        self.id = session_id
        self.redis = redis_inst

    def get_meta(self):
        raw = self.redis.hgetall(SessionManager.get_meta_key(self.id))
        res = {
            'hint_id': raw[b'hint_id'].decode(),
            'url': raw[b'url'].decode(),
            'total_tasks': int(raw[b'total_tasks']),
            'complete_tasks': int(raw[b'complete_tasks']),
            'failed_tasks': int(raw[b'failed_tasks']),
            'rejected_tasks': int(raw[b'rejected_tasks']),
            'crawled_content': int(raw[b'crawled_content']),
            'evaluated_content': int(raw[b'evaluated_content']),
        }
        return res

    def add_url(self, url):
        # urls are stored in sets
        res = self.redis.sadd(SessionManager.get_urls_key(self.id), url)
        if res:
            self.redis.hincrby(
                SessionManager.get_meta_key(self.id),
                'total_tasks', 1)
        return res == 1

    def has_url(self, url):
        res = self.redis.sismember(SessionManager.get_urls_key(self.id), url)
        # logger.info( f'has_url {res=} {type(res)=}')
        return res

    def add_content(self, url):
        return self.redis.sadd(SessionManager.get_content_key(self.id), url)

    def has_content(self, url):
        return self.redis.sismember(
            SessionManager.get_content_key(self.id),
            url)

    def inc_complete_urls(self):
        self.redis.hincrby(
            SessionManager.get_meta_key(self.id),
            'complete_tasks', 1)

    def inc_failed_urls(self):
        self.redis.hincrby(
            SessionManager.get_meta_key(self.id),
            'failed_tasks', 1)

    def inc_rejected_urls(self):
        self.redis.hincrby(
            SessionManager.get_meta_key(self.id),
            'rejected_tasks', 1)

    def inc_crawled_content(self):
        self.redis.hincrby(
            SessionManager.get_meta_key(self.id),
            'crawled_content', 1)

    def inc_evaluated_content(self):
        self.redis.hincrby(
            SessionManager.get_meta_key(self.id),
            'evaluated_content', 1)


class SessionManager:
    def __init__(self, host, port=6379, db=0, protocol=3):
        self.redis = redis.Redis(
            host=host, port=port, db=db, protocol=protocol
        )

    def is_ready(self) -> bool:
        try:
            self.redis.ping()
            return True
        except redis.exceptions.ConnectionError:
            return False

    def create(self, hint_id=0, url='') -> Session:
        session_id = self.gen_session_id()
        self.redis.hset(SessionManager.get_meta_key(session_id), mapping={
            'hint_id': hint_id,
            'url': url,
            'total_tasks': 0,
            'complete_tasks': 0,
            'failed_tasks': 0,
            'rejected_tasks': 0,
            'crawled_content': 0,
            'evaluated_content': 0,
        })
        # logger.info( f'hset result {r=} {type(r)=}')
        return Session(session_id, self.redis)

    def has(self, session_id) -> bool:
        res = self.redis.exists(SessionManager.get_meta_key(session_id))
        # logger.info( f'sessionmanager.has {res=} {type(res)=}')
        return res

    def get(self, session_id) -> Session:
        return Session(session_id, self.redis)

    def remove(self, session_id):
        self.redis.delete(SessionManager.get_meta_key(session_id))
        self.redis.delete(SessionManager.get_urls_key(session_id))
        self.redis.delete(SessionManager.get_content_key(session_id))

    def gen_session_id(self) -> str:
        # TODO: add existance check
        return md5(str(time.time()).encode()).hexdigest()

    @staticmethod
    def get_meta_key(session_id):
        return f'{SESSION_METADATA_KEY_PREFIX}{session_id}'

    @staticmethod
    def get_urls_key(session_id):
        return f'{SESSION_URLS_KEY_PREFIX}{session_id}'

    @staticmethod
    def get_content_key(session_id):
        return f'{SESSION_CONTENT_KEY_PREFIX}{session_id}'
