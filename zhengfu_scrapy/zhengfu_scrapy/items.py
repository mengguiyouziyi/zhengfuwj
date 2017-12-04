# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BJGovItem(scrapy.Item):
	cat = scrapy.Field()
	city = scrapy.Field()
	detail_url = scrapy.Field()
	title = scrapy.Field()
	cat_cls = scrapy.Field()
	art_org = scrapy.Field()
	art_date = scrapy.Field()
	imp_date = scrapy.Field()
	end_date = scrapy.Field()
	art_num = scrapy.Field()
	validity = scrapy.Field()
	pub_date = scrapy.Field()
	html = scrapy.Field()


class TJGovItem(scrapy.Item):
	f_cla = scrapy.Field()
	t_cla = scrapy.Field()
	city = scrapy.Field()
	detail_url = scrapy.Field()
	title = scrapy.Field()
	index_num = scrapy.Field()
	out_date = scrapy.Field()
	art_num = scrapy.Field()
	publisher = scrapy.Field()
	subcat = scrapy.Field()
	summary = scrapy.Field()
	html = scrapy.Field()


class SJZGovItem(scrapy.Item):
	cat = scrapy.Field()
	city = scrapy.Field()
	art_num = scrapy.Field()
	detail_url = scrapy.Field()
	title = scrapy.Field()
	out_date = scrapy.Field()
	html = scrapy.Field()
