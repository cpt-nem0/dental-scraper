# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    product_title = scrapy.Field()
    product_price = scrapy.Field()
    path_to_image = scrapy.Field()
