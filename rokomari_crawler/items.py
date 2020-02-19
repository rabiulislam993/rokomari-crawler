# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RokomariCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # seo_title = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    translator = scrapy.Field()
    editor = scrapy.Field()
    publisher = scrapy.Field()
    isbn = scrapy.Field()
    edition = scrapy.Field()
    no_of_page = scrapy.Field()
    country = scrapy.Field()
    language = scrapy.Field()

    price = scrapy.Field()
    category = scrapy.Field()
    book_url = scrapy.Field()
    book_id = scrapy.Field()
    book_slug = scrapy.Field()
    image_urls = scrapy.Field()
    description = scrapy.Field()


    images = scrapy.Field()
