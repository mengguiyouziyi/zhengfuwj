# -*- coding: utf-8 -*-
import scrapy, re, math
from scrapy.selector import Selector
from zhengfu_scrapy.items import TJGovItem
from util.info import startup_nodes
from rediscluster import StrictRedisCluster
from scrapy.exceptions import CloseSpider


class TouzishijianSpider(scrapy.Spider):
	name = 'tj_gov_slave'
	custom_settings = {
		'DEFAULT_REQUEST_HEADERS': {
			'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			'accept-encoding': "gzip, deflate",
			'accept-language': "zh-CN,zh;q=0.9",
			'cache-control': "no-cache",
			'connection': "keep-alive",
			# 'cookie': "UM_distinctid=15fed1a98f94c7-05e1931ccec53d-31657c00-13c680-15fed1a98fc9e5; CNZZDATA1261103251=754832092-1511507618-%7C1512105327",
			'host': "gk.tj.gov.cn",
			'upgrade-insecure-requests': "1",
			# 'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
			'postman-token': "4803f958-e8fb-a5f2-6157-10e1862285a1"
		},
		'DOWNLOADER_MIDDLEWARES': {
			'zhengfu_scrapy.middlewares.ProxyMiddleware': 1,
			'zhengfu_scrapy.middlewares.RetryMiddleware': 110,
			'zhengfu_scrapy.middlewares.RotateUserAgentMiddleware': 3,
		},
		# 'LOG_LEVEL': 'INFO'
	}

	def __init__(self):
		self.rc = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True)

	def start_requests(self):
		while True:
			comp = self.rc.rpop('zheng_tj_url')
			if not comp:
				raise CloseSpider('no datas')
			v_l = comp.split('~')
			f_cla = v_l[0]
			t_cla = v_l[1]
			detail_url = v_l[2]
			yield scrapy.Request(detail_url, meta={'f_cla': f_cla, 't_cla': t_cla}, dont_filter=False)

	def parse(self, response):
		f_cla = response.meta.get('f_cla')
		t_cla = response.meta.get('t_cla')
		select = Selector(text=response.text)
		index_num = select.xpath('//table[@class="table_key"]/tr[1]/td[2]/text()').extract_first()
		art_num = select.xpath('//table[@class="table_key"]/tr[2]/td[2]/text()').extract_first()
		out_date = select.xpath('//table[@class="table_key"]/tr[2]/td[4]/text()').extract_first()
		publisher = select.xpath('//span[@id="span_publisher"]/text()').extract_first()
		subcat = select.xpath('//span[@id="span_subcat"]/text()').extract_first()
		title = select.xpath('//span[@id="span_docTitle"]/text()').extract_first()
		summary = select.xpath('//div[@style="font-size:14px;line-height:25px;"]').extract_first()
		html = select.xpath('//div[@class="article_content_file"]').extract_first()
		item = TJGovItem()
		item['f_cla'] = f_cla
		item['t_cla'] = t_cla
		item['title'] = title
		item['detail_url'] = response.url
		item['index_num'] = index_num if index_num else ''
		item['out_date'] = out_date if out_date else ''
		item['art_num'] = art_num if art_num else ''
		item['publisher'] = publisher if publisher else ''
		item['subcat'] = subcat if subcat else ''
		item['summary'] = summary if summary else ''
		item['html'] = html
		item['city'] = '天津'
		yield item
