# -*- coding: utf-8 -*-
from scrapy.exporters import JsonLinesItemExporter
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
        
class PerCategoryExportPipeline(object):

	def open_spider(self, spider):
		self.category_to_exporter = {}

	def close_spider(self, spider):
		for exporter in self.category_to_exporter.values():
			exporter.finish_exporting()
			exporter.file.close()

	def _exporter_for_item(self, item):
		if 'category' in item.keys():
			category = item['category']
		else:
			category = 'reviews_of_'+item['review_category']
		
		if category not in self.category_to_exporter.keys():
			f = open(f'{category}.json', 'wb')
			exporter = JsonLinesItemExporter(f,indent=4)
			exporter.start_exporting()
			self.category_to_exporter[category] = exporter
		
		return self.category_to_exporter[category]

	def process_item(self, item, spider):
		
		exporter = self._exporter_for_item(item)
		del(item['image_urls'])
		del(item['images'][0]['url'])
		exporter.export_item(item)	
		return item
