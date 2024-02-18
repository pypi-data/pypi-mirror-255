import asyncio

# import json
# import re
# import traceback
import os
import time
from http.client import HTTPException
from threading import Thread
from typing import Dict, Tuple, TypeAlias

# from bs4 import BeautifulSoup
# from playwright.async_api import Locator, Page
from playwright.async_api import TimeoutError as PlaywriteTimeoutError
from playwright.async_api import async_playwright
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError as PytubeAgeRestrictedError

from ....common.logger import logger
from ....common.storage import BaseStorage
from ....common.types import (
    CrawlerBackTask,
    CrawlerContent,
    CrawlerNop,
    DatapoolContentType,
)
from ..base_plugin import BasePlugin, WorkerTask

URL: TypeAlias = str
TagID: TypeAlias = str
Timestamp: TypeAlias = float


class YoutubeChannelPlugin(BasePlugin):
    CHANNEL_CACHE_TTL = 3600  # seconds
    channel_tag_cache: Dict[URL, Tuple[Timestamp, TagID]] = {}
    channel_cache_lock: Dict[URL, asyncio.Lock] = {}
    channel_cache_lock_protection = asyncio.Lock()

    def __init__(self, ctx):
        super().__init__(ctx)

    @staticmethod
    def is_supported(url):
        u = BasePlugin.parse_url(url)
        # logger.info( f'dataphoenix.info {u=}')
        if u.netloc == "youtube.com" or u.netloc == "www.youtube.com":
            if u.path[0:2] == "/@":
                return True
            elif u.path[0:6] == "/watch" and u.query[0:2] == "v=":
                return True

        return False

    async def process(self, task: WorkerTask):
        logger.info(f"youtube_channel::process({task.url})")

        if task.content_type == DatapoolContentType.Video:
            yield await self.download_content(task.url, task.content_type)
            return

        channel_name = None
        video_id = None

        u = self.parse_url(task.url)

        if u.path[0:2] == "/@":
            channel_name = u.path.split("/")[1]
        elif u.path[0:6] == "/watch" and u.query[0:2] == "v=":
            video_id = u.query[2:13]
        else:
            raise Exception(f"unsupported {task.url=}")

        async with async_playwright() as playwright:
            webkit = playwright.chromium
            browser = await webkit.launch()
            context = await browser.new_context()

            page = await context.new_page()

            if channel_name is not None:
                tag_id = await self._get_channel_tag_id(channel_name, page)
                if not tag_id:
                    logger.info("No #description tag found, give up")
                    return
                if tag_id.is_crawling_allowed() is False:
                    logger.info("Crawling is now allowed by tag")
                    return

                logger.info(f"{tag_id=}")

                url = f"https://www.youtube.com/{channel_name}/videos"

                logger.info(f"loading url {url}")
                await page.goto(url)
                logger.info(f"loaded {url=}")

                logger.info("parsing feed")
                async for yielded in self._process_feed(url, page):
                    yield yielded

            elif video_id is not None:
                async for yielded in self._process_video(task.url, page, context):
                    yield yielded
            else:
                raise Exception("not implemented")

            await page.close()

    async def download_content(self, url, type: DatapoolContentType):
        if not await self.is_content_processed(url):
            storage_id = await self.download_video(url)
            if storage_id:
                return CrawlerContent(
                    type=type,
                    storage_id=storage_id,
                    url=url,
                )
        return CrawlerNop()

    def _download_thread(self, url, storage_id, state: dict):
        logger.info(f"_download_thread: {url=} {storage_id=}")

        youtube = YouTube(url)
        state["tmp_path"] = None
        try:
            video = (
                youtube.streams.filter(progressive=True, file_extension="mp4")
                .order_by("resolution")
                .first()
            )
            for i in range(0, 3):
                try:
                    state["tmp_path"] = video.download(
                        output_path="/tmp", filename=storage_id
                    )
                    break

                except HTTPException as e:
                    logger.error(f"HTTPException {e}")
                    # will try to download again after delay
                    time.sleep(5)  # TODO: should be configurable

        except PytubeAgeRestrictedError as e:
            logger.error(f"AgeRestrictedError exception {e}")
            # TODO: should be able to bypass this.
            # For now skip such videos

        logger.info(f"download done {storage_id=}")
        state["done"] = True

    async def _process_video(self, url, page, context):
        logger.info(f"_process_video {url=}")
        await page.goto(url)
        # logger.info(f"loaded {url=}")

        # find channel name, then will search for tag there
        channel_uri = page.locator("ytd-channel-name a:visible").filter(
            has_not=page.get_by_role("link", name="ManageEngine", exact=True)
        )
        channel_uri = await channel_uri.get_attribute("href")
        logger.info(f"{channel_uri=}")

        page2 = await context.new_page()
        tag_id = await self._get_channel_tag_id(channel_uri, page2)
        await page2.close()
        if not tag_id or tag_id.is_crawling_allowed() is False:
            return

        storage_id = await self.download_video(url)
        if storage_id:
            yield CrawlerContent(
                tag_id=str(tag_id),
                type=DatapoolContentType.Video,
                storage_id=storage_id,
                url=url,
            )

    async def download_video(self, url):
        storage_id = BaseStorage.gen_id(url)

        # ... .desc()

        download_state = {"done": False, "tmp_path": None}
        thread = Thread(
            target=self._download_thread,
            args=(url, storage_id, download_state),
        )
        thread.start()
        logger.info(f"started video download thread on {storage_id=}")
        while not download_state["done"]:
            await asyncio.sleep(1)
        thread.join()
        logger.info(f"finished video download thread on {storage_id=}")
        tmp_path = download_state["tmp_path"]

        if tmp_path:
            raw_video = open(tmp_path, "rb").read()

            await self.ctx.storage.put(storage_id, raw_video)
            # TODO: title and other meta data can be put into separate storage item ( for example storage_id+"_meta" ) as json
            # for displaying at openlicense.ai

            logger.info(f"put video into storage {storage_id=}")
            os.remove(tmp_path)

            return storage_id

    async def _get_channel_tag_id(self, channel_uri, page):
        # init channel_lock per channel_uri
        async with self.channel_cache_lock_protection:
            if channel_uri not in self.channel_cache_lock:
                self.channel_cache_lock[channel_uri] = asyncio.Lock()

        # mutexed access to channel_tag_cache per channel_uri
        async with self.channel_cache_lock[channel_uri]:
            # get from internal cache if exists and TTL is fine
            if channel_uri in self.channel_tag_cache:
                now = time.time()
                (then, tag_id) = self.channel_tag_cache[channel_uri]
                if now - then <= self.CHANNEL_CACHE_TTL:
                    logger.info(f"cached {tag_id=}")
                    return tag_id

            # else parse channel page
            tag_id = await self._parse_channel_tag_id(channel_uri, page)

            # add to cache
            now = time.time()
            self.channel_tag_cache[channel_uri] = (now, tag_id)

            logger.info(f"parsed {tag_id=}")
            return tag_id

    async def _parse_channel_tag_id(self, channel_uri, page):
        url = f"https://www.youtube.com/{channel_uri}/about"

        logger.info(f"loading url {url}")
        await page.goto(url)
        logger.info(f"loaded {url=}")

        return await BasePlugin.parse_meta_tag(page, "description")

    async def _process_feed(self, url, page):
        total_videos = 0
        # iter = 0
        while True:
            # logger.info( 'scrolling  to bottom')
            # await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # container = self.page.locator('.ytd-app#content')
            # await container.evaluate("node => {node.scrollTop=node.scrollHeight;}")
            # logger.info( 'scrolled')

            videos = await page.locator("ytd-rich-item-renderer").all()

            n = len(videos)
            logger.info(f"videos on page {n=}")

            i = total_videos
            while i < n:
                try:
                    href = (
                        await videos[i]
                        .locator("a#video-title-link")
                        .get_attribute("href", timeout=100)
                    )
                    title = (
                        await videos[i]
                        .locator("yt-formatted-string#video-title")
                        .text_content()
                    )

                    logger.info(f"{i=} {href=} {title=}")

                    video_url = "https://www.youtube.com" + href

                    # logger.info( f'---------yielding {video_url=}')
                    yield CrawlerBackTask(url=video_url)
                    # logger.info( f'---------yielded {video_url=}')

                    i += 1
                except PlaywriteTimeoutError as e:
                    # element may be not ready yet, no problems, will get it on the next iteration
                    # logger.info( 'get_attribute timeout' )
                    break

            total_videos = i

            # logger.info( 'creating button locator')
            spinner = page.locator("#spinner")

            # scroll to  bottom. (js window.scrollTo etc does not work for some reason..)
            await page.mouse.wheel(0, 600)

            # logger.info( 'getting disabled attr')
            spinner_exists = await spinner.count()

            # logger.info(f"{spinner_exists=}")
            if (
                not spinner_exists and n > 0 and total_videos == n
            ):  # all videos are processed
                logger.info("spinner gone, done")
                break

            await asyncio.sleep(1)

        yield CrawlerNop()
