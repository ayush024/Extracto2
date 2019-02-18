# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ExtractoItem(scrapy.Item):
	item_id = scrapy.Field()
	name = scrapy.Field()
	price = scrapy.Field()
	no_of_reviews = scrapy.Field()
	ratings = scrapy.Field()
	descriptions = scrapy.Field()
	image_urls = scrapy.Field()
	images = scrapy.Field()
	category = scrapy.Field()

class ExtractoReview(scrapy.Item):
	item_id = scrapy.Field()
	reviewed_by = scrapy.Field()
	rating = scrapy.Field()
	review = scrapy.Field()