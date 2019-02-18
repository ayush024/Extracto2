# -*- coding: utf-8 -*-
import scrapy
from Extracto.items import ExtractoItem

class Test3Spider(scrapy.Spider):
	name = 'test3'
	allowed_domains = ['amazon.com']
	next_page_count = 0
	
	start_urls = ['https://www.amazon.com/s?rh=n%3A172282%2Cn%3A!493964%2Cn%3A172623&page=5&qid=1550308509%29&ref=sr_pg_5']
	
	def parse(self, response):
	#	item = ExtractoItem()
	#	item['image_urls'] = [response.css('div#imgTagWrapperId img::attr(src)').extract_first().strip('\n')]
		detail_link = response.css('a.s-access-detail-page::attr(href)').extract()
		for link in detail_link:
			link = response.urljoin(link)
			yield scrapy.Request(link, callback = self.parse_item)	

		next_page_link = response.css('a#pagnNextLink::attr(href)').extract_first()
		if self.next_page_count < 2 and next_page_link:
			self.next_page_count += 1
			next_page_link = response.urljoin(next_page_link)
			yield scrapy.Request(next_page_link, callback = self.parse)
		
	def parse_item(self, response):
		name = response.css('span#productTitle::text').extract_first().strip('\n ')
		yield {'name': name}