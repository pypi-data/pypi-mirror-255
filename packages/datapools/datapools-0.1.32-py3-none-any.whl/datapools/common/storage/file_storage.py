import os

from ..logger import logger
from .base_storage import BaseStorage


class FileStorage(BaseStorage):
    def __init__(self, dst_path):
        self.dst_path = dst_path

    async def put(self, storage_id, content):
        with open(self.get_path(storage_id), "wb") as f:
            if type(content) is str:
                content = content.encode()
            f.write(content)

    async def get(self, storage_id):
        with open(self.get_path(storage_id), "rb") as f:
            res = f.read()
            return res

    async def remove(self, storage_id):
        path = self.get_path(storage_id)
        logger.info(f"unlink {path=}")
        os.unlink(path)
        
    async def has( self, storage_id):
        path = self.get_path(storage_id)
        return os.path.exists( path )

    def get_path(self, storage_id):
        return os.path.join(self.dst_path, storage_id)
