import asyncio
import json
import re

# from bs4 import BeautifulSoup
# from playwright.async_api import Locator, Page
from playwright.async_api import TimeoutError as PlaywriteTimeoutError
from playwright.async_api import async_playwright, expect

from ....common.logger import logger
from ....common.storage import BaseStorage
from ....common.types import (
    CrawlerBackTask,
    CrawlerContent,
    CrawlerNop,
    DatapoolContentType,
)
from ..base_plugin import BasePlugin, WorkerTask

# import traceback


class DataPhoenixInfoPlugin(BasePlugin):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.header_tag_id = None

    @staticmethod
    def is_supported(url):
        u = BasePlugin.parse_url(url)
        # logger.info( f'dataphoenix.info {u=}')
        return u.netloc == "dataphoenix.info"

    async def process(self, task: WorkerTask):
        logger.info(f"dataphoenix_info::process({task.url})")

        async with async_playwright() as playwright:
            self.webkit = playwright.webkit
            self.browser = await self.webkit.launch()
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

            # async with httpx.AsyncClient() as client:
            #     logger.info( f'loading url {url}')

            #     r = await client.get( url )
            #     #logger.info( f'got Response {r}')
            #     r = r.text
            logger.info(f"loading url {task.url}")
            await self.page.goto(task.url)  # "https://dataphoenix.info/news/"

            # check if <meta/> tag exists with our tag
            self.header_tag_id = await BasePlugin.parse_meta_tag(
                self.page, "robots"
            )
            logger.info(f"{self.header_tag_id=}")

            if not self.header_tag_id:
                logger.info("No <meta> tag found")
                return

            if self.header_tag_id.is_crawling_allowed() is False:
                logger.info("crawling disabled")
                return

            if re.match(
                "^http(s?)://dataphoenix.info/(news|papers|articles|videos)(?:$|/)",
                task.url,
            ):
                logger.info("parsing feed")
                async for yielded in self._process_feed(task.url):
                    yield yielded
            else:
                logger.info("parsing single page")
                async for yielded in self._process_single_page(task.url):
                    yield yielded

    async def _process_single_page(self, url):
        # article consists of header, excerpt and body
        # TODO: support video
        header = await self.page.locator("h1.c-post-header__title").all()
        if len(header) == 0:
            logger.error("Not parsable page (header)")
            # await self.page.screenshot(
            #     path="/app/tmp/not_parsable_page_header.png"
            # )
            return
        header = await header[0].inner_text()

        # optional Excerpt
        excerpt = await self.page.locator("p.c-post-header__excerpt").all()
        if len(excerpt) > 0:
            excerpt = await excerpt[0].inner_text()
        else:
            excerpt = ""

        body = ""
        ps = await self.page.locator("section.c-content > p").all()
        for p in ps:
            body += await p.inner_text() + "\n"

        storage_id = BaseStorage.gen_id(url)
        logger.info(f"putting article into {storage_id=}")

        await self.ctx.storage.put(
            storage_id,
            json.dumps({"header": header, "excerpt": excerpt, "body": body}),
        )

        yield CrawlerContent(
            tag_id=str(self.header_tag_id),
            type=DatapoolContentType.Text,
            storage_id=storage_id,
            url=url,
        )

    async def _process_feed(self, url):
        total_news = 0
        while True:
            # logger.info( 'scrolling  to bottom')
            # await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # logger.info( 'scrolled')

            urls = await self.page.locator("a.c-post-card__url").all()
            n = len(urls)
            logger.info(f"news on page {n=}")
            for i in range(total_news, n):
                href = await urls[i].get_attribute("href")
                yield CrawlerBackTask(url="https://dataphoenix.info" + href)

            total_news = n

            # logger.info( 'creating button locator')
            button = self.page.locator("button.js-load-posts")

            # logger.info( 'getting disabled attr')
            disabled = await button.get_attribute("disabled", timeout=0)

            logger.info(f"button disabled={disabled}")
            if disabled == "disabled":
                break

            ready = False
            for i in range(0, 2):
                try:
                    logger.info(
                        f"waiting until button is ready for clicks ({i})"
                    )
                    await button.click(trial=True, timeout=10000)
                    logger.info("button is ready for clicks")
                    ready = True
                    break
                except PlaywriteTimeoutError:
                    # logger.info( e )
                    # logger.info( traceback.format_exc() )
                    await self._try_remove_banner()

            if not ready:
                logger.error("ready wait failed error")
                # await self.page.screenshot(path="/app/tmp/screenshot.png")
                break

            try:
                await button.click(no_wait_after=True, timeout=10000)
                # logger.info( "clicked More Posts")
            except PlaywriteTimeoutError:
                logger.error("click More Posts timeout")
                # await self.page.screenshot(path="/app/tmp/screenshot.png")
                break

            button = self.page.locator("button.js-load-posts.c-btn--loading")
            await button.wait_for()
            logger.info("button changed to Loading")

            button = self.page.locator(
                "button.js-load-posts:not(.c-btn--loading)"
            )
            await button.wait_for()
            logger.info("button changed back to More Posts")

            await asyncio.sleep(1)

        yield CrawlerNop()

    async def _try_remove_banner(self):
        modal = await self.page.locator("div.hb-modal-content").all()
        if len(modal) == 0:
            logger.info("No modal found")
            return False

        logger.info("Modal found")

        close_button = await self.page.locator(
            'button[aria-label="close"]'
        ).all()
        if len(close_button) == 0:
            logger.error("Unexpected: modal without close button")
            return False

        logger.info("clicking modal close button")

        await close_button[0].click(no_wait_after=True)
        logger.info("waiting modal to dissapear")
        await expect(modal[0]).to_have_count(0)
        logger.info("dissapeared")
        return True
