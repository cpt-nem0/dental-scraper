# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import os
from datetime import datetime

import redis

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ScraperPipeline:
    def process_item(self, item, spider):
        return item


class JsonStoragePipeline:
    def __init__(self, filename: str = None):
        os.makedirs("data", exist_ok=True)

        if filename:
            self.filename = f"data/{filename}.json"
        else:
            # Generate filename with timestamp if no name provided
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = f"data/products_{timestamp}.json"

        self.file = None  # Don't open the file immediately
        self.products = []
        self.has_items = False

    def open_spider(self, spider):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.products = json.load(f)
            except json.JSONDecodeError:
                self.products = []

        self.file = open(self.filename, "r+")

    def process_item(self, item, spider):
        self.has_items = True
        self.products.append(dict(item))
        return item

    def close_spider(self, spider):
        if not self.file:
            return

        try:
            if self.has_items:
                json.dump(self.products, self.file)
        except Exception as e:
            raise e
        finally:
            self.file.close()

    @classmethod
    def from_crawler(cls, crawler):
        filename = crawler.settings.get("JSON_FILENAME")
        return cls(filename)


class RedisCachePipeline:
    def __init__(self):
        self.redis = redis.Redis()

    def process_item(self, item, spider):
        product_id = f"product:{item['product_title']}"

        # Check if price changed
        cached_price = self.redis.hget(product_id, "price")
        if cached_price and float(cached_price) == float(item["product_price"]):
            raise DropItem("Product price unchanged")

        # Update cache
        self.redis.hset(product_id, "price", item["product_price"])
        return item