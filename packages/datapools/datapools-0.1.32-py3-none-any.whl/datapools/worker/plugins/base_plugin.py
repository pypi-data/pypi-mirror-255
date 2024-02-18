import sys
import base64
from abc import abstractmethod, ABCMeta
from typing import AsyncGenerator, Union
from urllib.parse import urlparse, urljoin
import dns.resolver
from time import time
from PIL import Image
from PIL.ExifTags import Base as ExifTagsList
import io

import httpx

from ...common.logger import logger
from ...common.storage import BaseStorage
from ...common.types import (
    BaseCrawlerResult,
    DatapoolContentType,
    CrawlerContent,
    CrawlerNop,
    WorkerContext, 
    WorkerTask
)

try:
    from bs4 import BeautifulSoup
except ImportError:
    pass
try:
    from playwright.async_api import Page
except ImportError:
    pass
import re


class BasePluginException(Exception):
    pass


class BaseTag:
    _crawling_allowed = None
    _tag = None

    def __init__(self, tag, crawling_allowed=True):
        self._tag = tag
        self._crawling_allowed = crawling_allowed

    def __str__(self):
        return self._tag

    def __repr__(self):
        return f'BaseTag(tag={self._tag}, crawling allowed={self._crawling_allowed})'

    def is_crawling_allowed(self):
        return self._crawling_allowed


class CachedPairs:
    def __init__(self):
        self.data = {}

    def contains(self, key, ttl):
        return key in self.data and time() - self.data[key][1] < ttl

    def set(self, key, value):
        self.data[key] = (value, time())

    def get(self, key):
        return self.data[key][0]


class Cache:
    def __init__(self):
        self.value = None
        self.time = None

    def is_valid(self, ttl):
        return self.time is not None and time() - self.time < ttl

    def set(self, value):
        self.value = value
        self.time = time()

    def get(self):
        return self.value

    def __repr__(self):
        return f'Cache({self.value=}, {self.time=})'


class BasePlugin(metaclass=ABCMeta):
    license_filename = "LICENSE.txt"
    _busy_count = 0
    _is_busy = False
    _regexps = {
        re.compile(r"(?:^|.*\s)https://openlicense.ai/(t|n)/(\w+)"): True,
        # re.compile("olai\:(\w+)"): False,
    }
    copyright_tags_cache = CachedPairs()
    platform_tag_cache = Cache()

    def __init__(self, ctx: WorkerContext):
        self.ctx = ctx
        self._is_busy = False

    def __del__(self):
        if self._is_busy:
            self.is_busy = False  # calling @is_busy.setter
            logger.warning("was busy on destruction!!")

    @property
    def is_busy(self):
        return self._is_busy

    @is_busy.setter
    def is_busy(self, b: bool):
        self._is_busy = b
        if b:
            BasePlugin._busy_count += 1
            logger.info(
                f"busy count of plugins is {self._busy_count} (incremented)"
            )
        else:
            BasePlugin._busy_count -= 1
            logger.info(
                f"busy count of plugins is {self._busy_count} (decremented)"
            )

    async def download(self, url, headers={}, follow_redirects=True, max_redirects=5):
        logger.info(f'BasePlugin.download {url=}')
        try:
            async with httpx.AsyncClient(
                max_redirects=max_redirects
            ) as client:
                r = await client.get(
                    url, follow_redirects=follow_redirects, headers=headers
                )
                return r.content

        except Exception as e:
            logger.error(f"failed get content of {url}: {e}")

    async def download_content(self, url, type: DatapoolContentType):
        storage_id = BaseStorage.gen_id(url)

        content = await self.download(url)
        if content:
            logger.info(f'putting to {storage_id=}')
            await self.ctx.storage.put(storage_id, content)

            return CrawlerContent(
                    type=type,
                    storage_id=storage_id,
                    url=url,
            )
        return CrawlerNop()

    @staticmethod
    def parse_url(url):
        return urlparse(url)

    @staticmethod
    @abstractmethod
    def is_supported(url):
        pass

    @staticmethod
    def is_same_or_subdomain(dom1, dom2):
        if dom1 == dom2:
            return True
        s1 = dom1.split('.')
        s2 = dom2.split('.')
        return s1[-len(s2)::] == s2

    @staticmethod
    def get_local_url(href, page_url):
        pc = urlparse(page_url)
        p = urlparse(href)
        # print(p)
        if p.netloc == '' or BasePlugin.is_same_or_subdomain(
                p.netloc, pc.netloc):
            return urljoin(page_url, href)
        return False

    @staticmethod
    def merge_head_tail(head, tail):
        # returns intersection length
        m = len(head)
        n = len(tail)

        for i in range(max(0, m-n), m):
            head_slice = head[i:]
            tail_slice = tail[0:m-i]
            # print(i, head_slice, tail_slice)

            if head_slice == tail_slice:
                return head + tail[i:]
        return head + tail

    @abstractmethod
    async def process(
        self, task: WorkerTask
    ) -> AsyncGenerator[BaseCrawlerResult, None]:
        pass

    @staticmethod
    def is_imported(module):
        return module in sys.modules

    @classmethod
    def parse_dns_tag(cls, domain) -> Union[BaseTag, None]:
        logger.info(f'parse_dns_tag {domain=}')
        records = dns.resolver.resolve(domain, 'TXT')
        logger.info(f'{records=}')
        for record in records:
            tag = BasePlugin.parse_tag_in_str(str(record))
            if tag is not None:
                return tag
        return None

    @classmethod
    async def parse_meta_tag(cls, content, meta_name) -> Union[BaseTag, None]:
        if BasePlugin.is_imported("bs4") and type(content) is BeautifulSoup:
            return BasePlugin.parse_tag_in_bs_content(content, "meta")
        if (
            BasePlugin.is_imported("playwright.async_api")
            and type(content) is Page
        ):
            metas = content.locator(f'meta[name="{meta_name}"]')
            for meta in await metas.all():
                c = await meta.get_attribute("content")

                tag = BasePlugin.parse_tag_in_str(c)
                if tag is not None:
                    return tag
        return None

    @classmethod
    def parse_tag_in_str(cls, string) -> Union[BaseTag, None]:
        logger.info(f'parse_tag_in_str {string=}')
        for regexp, deniable in BasePlugin._regexps.items():
            tag = regexp.match(string)
            if tag is not None:
                if deniable is False:
                    return BaseTag(tag.group(1))
                else:
                    return BaseTag(tag.group(2), tag.group(1))
        return None

    @classmethod
    def parse_tag_in_bs_content(cls, content: BeautifulSoup, locator: str) -> Union[BaseTag, None]:
        for regexp, deniable in BasePlugin._regexps.items():
            tag = content.find(locator, attrs={"content": regexp})
            if tag is not None:
                if deniable is False:
                    return BaseTag(tag.group(1))
                else:
                    return BaseTag(tag.group(2), tag.group(1))
        return None

    @classmethod
    async def parse_tag_in(cls, content, locator: str = "") -> Union[BaseTag, None]:
        if type(content) is str:
            return BasePlugin.parse_tag_in_str(content)
        elif BasePlugin.is_imported("bs4") and type(content) is BeautifulSoup:
            return BasePlugin.parse_tag_in_bs_content(content, locator)

        elif (
            BasePlugin.is_imported("playwright.async_api")
            and type(content) is Page
        ):
            elems = content.locator(locator)
            for elem in await elems.all():
                c = await elem.text_content()
                if c is not None:
                    return BasePlugin.parse_tag_in_str(c)
        return None

    @staticmethod
    def get_content_type_by_mime_type(mime):
        logger.info(f"{mime=}")
        parts = mime.split("/")
        if parts[0] == "image":
            return DatapoolContentType.Image
        if parts[0] == "video":
            return DatapoolContentType.Video
        if parts[0] == "audio":
            return DatapoolContentType.Audio
        if parts[0] == "text" or mime == "application/json":
            return DatapoolContentType.Text

        raise BasePluginException(f"not supported {mime=}")

    @classmethod
    def parse_image_tag(cls, content) -> Union[BaseTag, None]:
        # load image from bytes content, parse Copyright exif field for a license tag
        try:
            image = Image.open(io.BytesIO(content))
            exifdata = image.getexif()
            cp = exifdata.get(ExifTagsList.Copyright)
            # logger.info( f'{cp=} {type(cp)=}')

            if type(cp) is str:
                return cls.parse_tag_in_str(cp)
        except Exception as e:
            logger.error(f'Failed process image: {e}')
        return None

    async def get_platform_tag(self, domain, content, ttl=3600, meta_name=None) -> Union[BaseTag, None]:
        # logger.info( f'get_platform_tag {self.platform_tag_cache=}')
        # logger.info(f'now={time()}' )
        # logger.info(f'diff={time() - self.platform_tag_cache.time if self.platform_tag_cache.time is not None else "nan"}')

        if not self.platform_tag_cache.is_valid(ttl):
            dns_tag = BasePlugin.parse_dns_tag(domain)
            if dns_tag:
                self.platform_tag_cache.set(dns_tag)
            else:
                # check if <meta/> tag exists with our tag
                header_tag = await BasePlugin.parse_meta_tag(content, meta_name)
                self.platform_tag_cache.set(header_tag)
        return self.platform_tag_cache.get()

    async def is_content_processed(self, url):
        if self.ctx.session.has_content(url):
            logger.info('content was processed already')
            return True
        return False

    @staticmethod
    async def get_webpage_image_bytes(img_locator):
        """for playwright only"""
        b64 = await img_locator.evaluate('(img) => {\
            img.crossOrigin="anonymous";\
            var canvas = document.createElement("canvas");\
            canvas.width = img.width;\
            canvas.height = img.height;\
            var ctx = canvas.getContext("2d");\
            ctx.drawImage(img, 0, 0);\
            var dataURL = canvas.toDataURL("image/png");\
            return dataURL;\
        }')
        return base64.b64decode(b64[len('data:image/png;base64,'):])
