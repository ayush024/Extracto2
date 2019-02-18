# -*- coding: utf-8 -*-
import scrapy
from Extracto.items import ExtractoItem, ExtractoReview
import re

class Test1Spider(scrapy.Spider):
	name = 'test1'
	allowed_domains = ['amazon.com']

	categories, urls = [], []
	next_page_count, review_page_count, item_count = 0,0,1

	start_urls = ['https://www.amazon.com/s/browse/ref=nav_shopall-export_nav_mw_sbd_intl_electronics?_encoding=UTF8&node=16225009011']

	def parse(self, response):
		if response.css('title::text').extract_first() == 'International Shopping: Shop Electronics that Ship Internationally':
			divs = response.css('div.acs_tile__content')
			if not self.categories:
				for div in divs:
					url = div.css('a::attr(href)').extract_first()
					self.categories.append(div.css('span::text').extract_first().strip('\n').strip('\t').strip('\n'))
					self.urls.append(response.urljoin(url))
			
			for i in range(len(self.urls)):
				request = scrapy.Request(self.urls[i], callback = self.parse_category)
				request.meta['category'] = self.categories[i]
				yield request

	def parse_category(self, response):	

		category = response.meta['category']
		detail_link = response.css('a.s-access-detail-page::attr(href)').extract()
		for link in detail_link:
			link = response.urljoin(link)
			request = scrapy.Request(link, callback = self.parse_item)
			request.meta['category'] = category
			yield request 

		next_page_link = response.css('a#pagnNextLink::attr(href)').extract_first()
		if self.next_page_count < 3 and next_page_link:
			self.next_page_count += 1
			request = scrapy.Request(response.urljoin(next_page_link), callback = self.parse_category)
			request.meta['category'] = category
			yield request
		else:
			self.next_page_count = 0

	def parse_item(self, response):	
		item = ExtractoItem()
		try:
			name = response.css('span#productTitle::text').extract_first().strip('\n ')
			price = response.css('span#priceblock_ourprice::text').extract_first()
			if name == None or price == None or ' ' in price:
				raise Exception
		except:
			return None		
		
		else:
			item['item_id'] = self.item_count
			self.item_count += 1
			item['name'] = name
			item['price'] = ''
			for fragment in price.strip('$').split(','):
				item['price'] = item['price'] + fragment.strip(',')
			item['price'] = float(item['price'])	

		item['category'] = response.meta['category']

		no_of_reviews = response.css('span#acrCustomerReviewText::text').extract_first()
		item['no_of_reviews'] = 0 if no_of_reviews==None else no_of_reviews.strip(' customer reviews')

		ratings = response.css('i.a-icon-star span.a-icon-alt::text').extract_first()
		item['ratings'] = None if ratings==None else float(ratings.split(' ')[0])
	
		#for image	
		item['image_urls'] = [response.css('div#imgTagWrapperId img::attr(src)').extract_first().strip('\n')]				
		
		#for descriptions
		item['descriptions'] = []
		raw_descriptions = response.css('div#feature-bullets ul.a-unordered-list li span.a-list-item::text').extract()
		if raw_descriptions:
			for desc in raw_descriptions:
				desc = desc.strip(' \n\t')
				if desc != '':
					item['descriptions'].append(desc)
		yield item

		if response.css('div.a-section.review'):
			request = scrapy.Request(response.url, callback=self.parse_reviews)
			request.meta['item_id'] = item['item_id']
			request.meta['category'] = item['category']
			yield request 
			
	def parse_reviews(self, response):
		item = ExtractoReview()
		item['item_id'] = response.meta['item_id']
		item['review_category'] = response.meta['category']

		divs = response.css('div.a-section.review')
		for div in divs:
			item['reviewed_by'] = div.css('span.a-profile-name::text').extract_first()		
			rating = div.css('span.a-icon-alt::text').extract_first()
			if rating:
				item['rating'] = rating.split(' ')[0]
			else:
				item['rating'] = None
			if re.search('Customer reviews', response.css('title::text').extract_first()):
				item['review'] = div.css('span.review-text::text').extract_first()
			else:
				item['review'] = div.css('div.a-expander-content::text').extract_first()
			yield item
			
		if response.css('a.a-link-emphasis'):
			next_link = response.css('a.a-link-emphasis::attr(href)').extract_first()
		elif response.css('li.a-last a'):
			next_link = response.css('li.a-last a::attr(href)').extract_first()
		else: 
			next_link = None		
		if next_link and self.review_page_count < 2:
			self.review_page_count += 1
			request = scrapy.Request(response.urljoin('next_link'), callback=self.parse_reviews)
			request.meta['item_id'] = item['item_id']
			request.meta['review_category'] = item['review_category']
			yield request
		else:
			self.review_page_count = 0