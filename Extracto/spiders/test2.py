# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
import json
import re
import mysql.connector
#from scrapy_splash import SplashRequest
#db = mysql.connector.connect(host = "localhost",
#			user = "root",
#			password = "root",
#			db = "ecommerce")
#cur = db.cursor()

class Test2Spider(scrapy.Spider):
	name = 'test2'
	allowed_domains = ['amazon.com']
#	lua_script = """

	img_dict = {}
	counter = 0

	start_urls = ['https://www.amazon.com/s/ref=s9_acss_bw_cts_AEElectr_T1_w?fst=as%3Aoff&rh=n%3A172282%2Cp_n_shipping_option-bin%3A3242350011%2Cn%3A!493964%2Cn%3A281407&bbn=493964&ie=UTF8&qid=1486423355&rnid=493964&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-4&pf_rd_r=2TQYAKRSVMJ90S66ZGV0&pf_rd_t=101&pf_rd_p=82d03e2f-30e3-48bf-a811-d3d2a6628949&pf_rd_i=16225009011']

	def parse(self, response):
		detail_link = response.css('a.s-access-detail-page::attr(href)').extract()
		for link in detail_link:
			link = response.urljoin(link)
			yield scrapy.Request(link, callback = self.parse_item)

		while self.counter<6:
			if self.counter!=5:
				next_page_link = response.css('a#pagnNextLink::attr(href)').extract_first()
				if next_page_link:
					next_page_link = response.urljoin(next_page_link)
					self.counter += 1
					yield scrapy.Request(next_page_link, callback = self.parse)
			else: 
				yield self.imgindex(self.img_dict)		
		
	def parse_item(self, response):	
		name = response.css('span#productTitle::text').extract_first().strip('\n ')
		price = response.css('span#priceblock_ourprice::text').extract_first()

		no_of_reviews = response.css('span#acrCustomerReviewText::text').extract_first()
		no_of_reviews = 0 if no_of_reviews==None else int(no_of_reviews.strip(' customer reviews'))

		ratings = response.css('i.a-icon-star span.a-icon-alt::text').extract_first()
		ratings = None if ratings==None else float(ratings.split(' ')[0])
	
		#for image	
		image = response.css('div#imgTagWrapperId img::attr(src)').extract_first().strip('\n')
		self.img_dict[len(self.img_dict)+1] = image
		image_index = len(self.img_dict) 				
		
		#for descriptions
		descriptions = []
		raw_descriptions = response.css('div#feature-bullets ul.a-unordered-list li span.a-list-item::text').extract()
		for desc in raw_descriptions:
			desc = desc.strip(' \n\t')
			if desc != '':
				descriptions.append(desc)
		yield {
			'name': name,
			'category': 'Accessories & Supplies',
			'price': price,
			'Total Reviews': no_of_reviews,
			'ratings': ratings,
			'image_source': image_index,
			'descriptions': descriptions 	
		}
			
		if response.css('div.a-section.review'):
			yield scrapy.Request(response.url, callback=self.parse_reviews)

	def parse_reviews(self, response):
		if response.css('a.a-link-emphasis'):
			yield scrapy.Request(response.urljoin(response.css('a.a-link-emphasis::attr(href)').extract_first()), callback=self.parse_reviews)
		else:	
			divs = response.css('div.a-section.review')
			reviews = []
		
			for div in divs:
				reviewed_by = div.css('span.a-profile-name::text').extract_first()		
				rating = div.css('span.a-icon-alt::text').extract_first().split(' ')[0]
				if re.search('Customer reviews', response.css('title::text').extract_first()):
					review = div.css('span.review-text::text').extract_first()
				else:
					review = div.css('div.a-expander-content::text').extract_first()
				reviews.append({'reviewed_by': reviewed_by, 'rating': rating, 'review': review})
			
			next_link = response.css('li.a-last a::attr(href)').extract_first()
			if next_link:
				yield scrapy.Request(response.urljoin('next_link'), callback=self.parse_reviews)
			else:
				yield {'reviews': reviews}
		 
	def imgindex(self, dictionary):

		with open('imgSrcIndex.json', 'w') as outfile:  
    			json.dump(dictionary, outfile)	
