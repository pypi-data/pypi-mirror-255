from abc import abstractmethod
from hashlib import md5


class BaseStorage:
    @abstractmethod
    async def put(self, storage_id, content):
        raise Exception("implement put()")

    @abstractmethod
    async def get(self, storage_id):
        raise Exception("implement get()")

    @abstractmethod
    async def remove(self, storage_id):
        raise Exception("implement remove()")

    @abstractmethod
    async def has(self, storage_id):
        raise Exception("implement has()")

    @staticmethod
    def gen_id(data):
        return md5(data.encode()).hexdigest()
