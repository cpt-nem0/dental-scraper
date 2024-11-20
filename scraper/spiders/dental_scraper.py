import asyncio
import json
import random

import scrapy
import websockets

from ..items import Product


class DentalCrawler(scrapy.Spider):
    name = "dental_crawler"
    allowed_domains = ["dentalstall.com"]

    def __init__(
        self,
        max_pages: int = None,
        proxies: str = None,
        notify_websocket_uri: str = None,
        start_url: str = "https://dentalstall.com/shop",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.max_pages = int(max_pages) if max_pages else float("inf")
        self.page_count = 0
        self.proxies = proxies.split(",") if proxies else []
        self.notify_websocket_uri = notify_websocket_uri

        self.items_scraped = 0

        self.proxy = random.choice(proxies) if self.proxies else ""

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse,
            meta={"proxy": self.proxy} if self.proxy else {},
        )

    def parse(self, response):
        self.page_count += 1

        # Extract products
        for product in response.css("div.product-inner"):

            self.items_scraped += 1

            yield Product(
                product_title=product.css(
                    "div.mf-product-thumbnail img::attr(title)"
                ).get(),
                product_price=product.css("div.mf-product-details bdi::text").get(),
                image_url=product.css(
                    "div.mf-product-thumbnail img::attr(data-lazy-src)"
                ).get(),
                local_path=None,
            )

        # Check page limit
        if self.page_count >= self.max_pages:
            self.logger.info(f"Reached maximum page limit of {self.max_pages}")
            return

        # pagination
        next_page = response.css("a.next.page-numbers::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse,
                meta={"proxy": self.proxy} if self.proxy else {},
            )

    async def __send_notification(self, ws_uri: str, message: dict):
        try:
            async with websockets.connect(ws_uri) as ws:

                await ws.send(json.dumps(message))
                response = await ws.recv()
                return response
        except asyncio.TimeoutError:
            self.logger.error(f"WebSocket connection timed out for URL: {ws_uri}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        return None

    def closed(self, reason):
        message = {
            "status": f"Scraping completed for crawler {self.name}, Reason: {reason}",
            "total_items_scraped": self.items_scraped,
            "total_items_saved": self.items_scraped,
            "total_pages_scraped": self.page_count,
        }

        if not self.notify_websocket_uri:
            self.logger.warning("WebSocket URL not provided in settings.")
            return

        async def notify():
            response = await self.__send_notification(
                self.notify_websocket_uri, message
            )
            if response:
                self.logger.info(f"Result notified, response from ws: {response}")
            else:
                self.logger.warning("Failed to send notification.")

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(notify())  # Schedule the task in the current event loop
        except RuntimeError:
            asyncio.run(notify())  # Run the coroutine if no event loop exists
