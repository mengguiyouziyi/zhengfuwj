# -*- coding: utf-8 -*-
import scrapy, re
from urllib.parse import urljoin
from scrapy.selector import Selector
from zhengfu_scrapy.items import SJZGovItem


class TouzishijianSpider(scrapy.Spider):
	name = 'sjz_gov'
	custom_settings = {
		'DEFAULT_REQUEST_HEADERS': {
			'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			'accept-encoding': "gzip, deflate",
			'accept-language': "zh-CN,zh;q=0.8",
			'cache-control': "no-cache",
			'connection': "keep-alive",
			# 'cookie': "__jsluid=c3e9cb688687876365a1e32a6c900e99; wdcid=38ee462d0967b535; yunsuo_session_verify=80cca22f1f7383725ac4094b3f88a648; _gscs_1023273986=t115059264ocr2z23|pv:1; _gscbrs_1023273986=1; wdlast=1511505926; _gscu_1023273986=11494946g8565p18",
			'host': "zhengce.beijing.gov.cn",
			'referer': "http://zhengce.beijing.gov.cn/library/192/33/50/438650/index.html",
			'upgrade-insecure-requests': "1",
			# 'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
			'postman-token': "31d69615-9944-caad-06a1-ba5fb209ddf1"
		}
	}

	def start_requests(self):
		zfwj_url = 'http://www.sjz.gov.cn/col/1490941083922/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '政府文件'})
		zfwj_url = 'http://www.sjz.gov.cn/col/1490941281206/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '政府函件'})
		zfwj_url = 'http://www.sjz.gov.cn/col/1490941325451/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '政府办公厅文件'})
		zfwj_url = 'http://www.sjz.gov.cn/col/1490941375792/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '政府办公厅函件'})
		zfwj_url = 'http://www.sjz.gov.cn/col/1500259049961/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '人事任免'})
		zfwj_url = 'http://www.sjz.gov.cn/col/1490942103503/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '政府公报'})
		zfwj_url = 'http://www.sjz.gov.cn/col/1490942121483/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '石家庄地方法规规章'})
		zfwj_url = 'http://www.sjz.gov.cn/col/1490942171264/index.html'
		yield scrapy.Request(zfwj_url, meta={'cat': '政策解读'})

	def parse(self, response):
		cat = response.meta.get('cat')
		select = Selector(text=response.text)
		li_s = select.xpath('//div[@class="list list_1 list_2"]/ul/li')
		for li in li_s:
			item = SJZGovItem()
			a = li.xpath('./a')
			detail_url = a.xpath('./@href').extract_first()
			art_num = a.xpath('./font/text()').extract_first().replace('[', '').replace(']', '')
			title = a.xpath('./text()').extract_first().strip()
			out_date = li.xpath('./span[@class="date"]/text()').extract_first()
			item['cat'] = cat
			item['detail_url'] = detail_url
			item['art_num'] = art_num
			item['city'] = art_num
			item['title'] = title
			item['out_date'] = out_date
			yield scrapy.Request(detail_url, callback=self.parse_detail, meta={'item': item})

	def parse_detail(self, response):
		item = response.meta.get('item')
		select = Selector(text=response.text)
		html = select.xpath('//div[@id="conN"]').extract_first()
		item['html'] = html
		yield item


def re_sub(vl):
	return re.sub(r'\[.*\]', '', _uniteList(vl), 1)


def _solSpace(s):
	return s.strip().replace('\t', '').replace('\r', '').replace('\n', '').replace('　----', '').replace('----', '')


def _uniteList(vl):
	vl_1 = ''.join([_solSpace(v) for v in vl if v]) if vl else ''
	return vl_1
