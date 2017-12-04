# -*- coding: utf-8 -*-
import scrapy, re, math
from scrapy.selector import Selector
# from zhengfu_scrapy.items import TJGovItem
from util.info import startup_nodes
from rediscluster import StrictRedisCluster


class TouzishijianSpider(scrapy.Spider):
	name = 'tj_gov_test'
	custom_settings = {
		# 'DEFAULT_REQUEST_HEADERS': {
		# 	'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		# 	'accept-encoding': "gzip, deflate",
		# 	'accept-language': "zh-CN,zh;q=0.9",
		# 	'cache-control': "no-cache",
		# 	'connection': "keep-alive",
		# 	'cookie': "UM_distinctid=15fed1a98f94c7-05e1931ccec53d-31657c00-13c680-15fed1a98fc9e5; CNZZDATA1261103251=754832092-1511507618-%7C1512105327",
		# 	'cookie': "JSESSIONID=4EBE67DEB69706501CEDBD19D45CDEF2; UM_distinctid=15fed1a98f94c7-05e1931ccec53d-31657c00-13c680-15fed1a98fc9e5; CNZZDATA1261103251=754832092-1511507618-%7C1512374430",
			# 'host': "gk.tj.gov.cn",
			# 'upgrade-insecure-requests': "1",
			# 'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
			# 'postman-token': "4803f958-e8fb-a5f2-6157-10e1862285a1"
		# },
		# 'DOWNLOADER_MIDDLEWARES': {
			# 'zhengfu_scrapy.middlewares.ProxyMiddleware': 1,
			# 'zhengfu_scrapy.middlewares.RetryMiddleware': 110,
			# 'zhengfu_scrapy.middlewares.RotateUserAgentMiddleware': 3,
		# },
		'LOG_LEVEL': 'INFO'
	}

	def start_requests(self):
		n_url = 'http://gk.tj.gov.cn/govsearch/search.jsp?page=%(page)s&ztfl=%(num)s' % {
			'page': 1,
			'num': 200
		}
		# payload = 'SType=1&searchColumn=&searchYear=&preSWord=&sword=&searchAgain=&page=%(page)s&pubURL=&ztfl=%(num)s' % {
		# 	'page': 3,
		# 	'num': 200
		# }
		yield scrapy.Request(n_url, callback=self.parse_next)

	def parse_next(self, response):
		with open('y.html', 'w') as f:
			f.writelines(response.text)
