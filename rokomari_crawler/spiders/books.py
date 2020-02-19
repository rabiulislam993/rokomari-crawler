# -*- coding: utf-8 -*-
import csv
import re

import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader

from rokomari_crawler.items import RokomariCrawlerItem

html_tags = re.compile('<.*?>')
book_detail_page_url_pattern = re.compile(r"rokomari.com/book/[\d]+/")


def is_book_detail_page_url(url):
    return bool(re.search(book_detail_page_url_pattern, url))


def book_info_a(response, value):
    try:
        return response.xpath('//td[text()="{}"]/following-sibling::td/a/text()'.format(value)).extract_first().strip()
    except:
        return ''


def book_info(response, value):
    try:
        return response.xpath('//td[text()="{}"]/following-sibling::td/text()'.format(value)).extract_first().strip()
    except:
        return ''


# scrapy crawl books -o data.csv -t csv


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['rokomari.com']

    def __init__(self):
        urls_csv_file = "rokomari_book_urls.csv"
        self.start_urls = []

        with open(urls_csv_file) as book_urls_file:
            book_urls = csv.DictReader(book_urls_file)
            for raw in book_urls:
                self.start_urls.append(raw["url"])

    def parse(self, response):
        if is_book_detail_page_url(response.request.url):
            yield self.parse_book(response, is_detail_page_url=True)

        else:
            books = response.xpath('//*[starts-with(@class, "book-list-wrapper")]')
            for book in books:
                book_url = book.xpath('.//a/@href').extract_first()
                book_absolute_url = response.urljoin(book_url)
                yield Request(book_absolute_url, callback=self.parse_book, meta={'URL': book_absolute_url,})

            next_page_url = response.xpath('//a[text()="Next"]/@href').extract_first()
            absolute_next_page_url = response.urljoin(next_page_url)
            yield Request(absolute_next_page_url, callback=self.parse)
    
    def parse_book(self, response, is_detail_page_url=False):
        l = ItemLoader(item=RokomariCrawlerItem(), response=response)
        title = book_info(response, 'Title')

        author = book_info_a(response, 'Author')
        translator = book_info_a(response, 'Translator')
        editor = book_info_a(response, 'Editor')
        publisher = book_info_a(response, 'Publisher')
        isbn = book_info(response, 'ISBN')
        edition = book_info(response, 'Edition')
        no_of_page = book_info(response, 'Number of Pages')
        country = book_info(response, 'Country')
        language = book_info(response, 'Language')

        category = response.xpath('//div[contains(@class, "details-book-info__content-category")]//a/text()').get().strip()
        price = response.xpath('//span[@class="sell-price"]/text()').extract_first().strip().split()[1]
        price = price.replace(",", "")

        if is_detail_page_url:
            book_url = response.request.url
        else:
            book_url = response.meta.get('URL')
        book_id, book_slug = book_url.split("/")[4:6]

        image_urls = response.xpath('//div[@class="look-inside-bg"]/following-sibling::img/@src').extract_first()
        if image_urls is None:
            image_urls = response.xpath('//div[@class="col-5 details-book-main-img-wrapper "]/img/@src').extract_first()
        if image_urls is None:
            image_urls = response.css('div.details-book-main-img-wrapper').xpath("./div/img/@src").extract_first()

        description = response.xpath('//div[@id="book-additional-description"]//div//p').get()
        if description and not re.sub(html_tags, "", description).strip():
            description = None  # remove empty <p> tags

        seo_title = response.xpath('//title/text()').get().strip()
        if seo_title:
            # format
            seo_title_list = seo_title.split("|")
            if len(seo_title_list) == 3:
                ban, eng, _ = seo_title.split("|")
                seo_title = ban.strip() + " (" + eng.strip()[4:-7] + ")"
            else:
                eng, _ = seo_title.split("|")
                seo_title = eng.strip()[4:-7]

        l.add_value('seo_title', seo_title)
        l.add_value('title', title)
        l.add_value('author', author)
        l.add_value('translator', translator)
        l.add_value('editor', editor)
        l.add_value('publisher', publisher)
        l.add_value('isbn', isbn)
        l.add_value('edition', edition)
        l.add_value('no_of_page', no_of_page)
        l.add_value('country', country)
        l.add_value('language', language)
        l.add_value('category', category)
        l.add_value('price', price)
        l.add_value('book_url', book_url)
        l.add_value('book_id', book_id)
        l.add_value('book_slug', book_slug)
        
        l.add_value('image_urls', image_urls)

        l.add_value('description', description)

        return l.load_item()


