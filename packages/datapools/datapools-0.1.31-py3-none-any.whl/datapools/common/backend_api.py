from typing import List

import httpx
from pydantic import BaseModel

from ..common.logger import logger
from ..common.types import CrawlerHintURLStatus  # , DatapoolRules


# class TagDatapool(BaseModel):
#     id: int
#     rules: DatapoolRules

#     class Config:
#         validate_assignment = True


class BackendAPI:
    def __init__(self, url):
        self.url = url

    async def get_hint_urls(self, limit):
        return await self.get_uri("get-hint-urls", {"limit": limit})

    async def set_hint_url_status(self, hint_id, status: CrawlerHintURLStatus, session_id=None):
        return await self.get_uri(
            "set-hint-url-status", {"id": hint_id, "status": status.value, "session_id": session_id}
        )

    # async def add_crawler_contents( self, contents: dict ):
    #     return await self.get_uri( 'add-crawler-contents', { 'contents': contents } )

    # async def get_crawled_contents(self, limit):
    #     return await self.get_uri( 'get-crawled-contents', { 'limit': limit } )

    async def add_crawled_content(self, data):
        return await self.get_uri("add-crawled-content", data)

    # async def get_tag_datapools(self, tag_id) -> List[TagDatapool]:
    #     res = await self.get_uri(
    #         "get-tag-datapools", {"filter": {"tag_id": tag_id}}
    #     )
    #     # logger.info( f"get_tag_datapools {res=}")
    #     for i in range(len(res)):
    #         res[i] = TagDatapool.parse_obj(res[i])
    #     return res

    async def get_uri(self, uri, data={}):
        async with httpx.AsyncClient() as client:
            url = self.url + uri
            logger.info(f"posting to {url=} {data=}")

            try:
                r = await client.post(url, json=data)
                if r.status_code == 200:
                    return r.json()
                else:
                    logger.error(f"Non 200 http response {r=}")
                    raise Exception("non 200 response")
            except httpx.ConnectError as e:
                logger.error( f'Failed connect Backend API server: {e}')
