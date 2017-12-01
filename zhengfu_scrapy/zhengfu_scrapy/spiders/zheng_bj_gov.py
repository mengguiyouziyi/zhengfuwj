# -*- coding: utf-8 -*-
import scrapy, re
from urllib.parse import urljoin
from scrapy.selector import Selector
from zhengfu_scrapy.items import BJGovItem


class TouzishijianSpider(scrapy.Spider):
	name = 'bj_gov'
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
		fb_url = 'http://zhengce.beijing.gov.cn/library/192/33/50/438650/index.html'
		yield scrapy.Request(fb_url, meta={'cat': '政策发布'})
		jd_url = 'http://zhengce.beijing.gov.cn/library/192/34/738532/index.html'
		yield scrapy.Request(jd_url, meta={'cat': '政策解读'})

	def parse(self, response):
		cat = response.meta.get('cat')
		select = Selector(text=response.text)
		li_tags = select.xpath('//div[@class="list xlfl_list"]/ul/li')
		# detail_urls = select.xpath('//div[@class="list xlfl_list"]/ul/li/a/@href').extract()
		# detail_urls = [urljoin(response.url, url) for url in detail_urls if url]
		for li in li_tags:
			ttitle = li.xpath('./a/text()').extract_first()
			ttitle = ttitle.strip() if ttitle else ''
			pdate = li.xpath('./span/text()').extract_first()
			pdate = pdate.strip() if pdate else ''
			url = li.xpath('./a/@href').extract_first()
			url = urljoin(response.url, url)
			yield scrapy.Request(url, callback=self.parse_detail, meta={'cat': cat, 'ttitle': ttitle, 'pdate': pdate})
		a = select.xpath('//div[@class="fy"]/div[last()]/a')
		n_text = a.xpath('./text()').extract_first()
		if '下一页' not in n_text:
			return
		n_url = a.xpath('./@href').extract_first()
		yield scrapy.Request(urljoin(response.url, n_url), meta={'cat': cat})

	def parse_detail(self, response):
		cat = response.meta.get('cat')
		ttitle = response.meta.get('ttitle')
		pdate = response.meta.get('pdate')
		select = Selector(text=response.text)
		ol = select.xpath('//ol[@class="zc_about clearfix"]')
		cat_cls = ol.xpath('./li[1]//text()').extract()
		cat_cls = re_sub(cat_cls)
		art_org = ol.xpath('./li[2]//text()').extract()
		art_org = re_sub(art_org)
		art_date = ol.xpath('./li[3]//text()').extract()
		art_date = re_sub(art_date)
		imp_date = ol.xpath('./li[4]//text()').extract()
		imp_date = re_sub(imp_date)
		end_date = ol.xpath('./li[5]//text()').extract()
		end_date = re_sub(end_date)
		art_num = ol.xpath('./li[6]//text()').extract()
		art_num = _uniteList(art_num)
		art_num = art_num.replace('[发文字号]', '')
		validity = ol.xpath('./li[7]//text()').extract()
		validity = re_sub(validity)
		pub_date = ol.xpath('./li[8]//text()').extract()
		pub_date = re_sub(pub_date) if pub_date else pdate
		html_tag = select.xpath('//div[@class="zc_con"]').extract()
		# title = select.xpath('//div[@class="zc_con"]/h1/text()').extract()
		# title = ''.join([t.strip().replace('"', '') for t in title if t]) if title else ''
		# intro = select.xpath('//*[@id="c_text"]//text()').extract()
		# intro = sol(intro)
		item = BJGovItem()
		item['cat'] = cat
		item['city'] = '北京'
		item['detail_url'] = response.url
		item['title'] = ttitle
		item['cat_cls'] = cat_cls
		item['art_org'] = art_org
		item['art_date'] = art_date
		item['imp_date'] = imp_date
		item['end_date'] = end_date
		item['art_num'] = art_num
		item['validity'] = validity
		item['pub_date'] = pub_date
		item['html'] = html_tag

		yield item


# def sol(ext):
# 	s = ''.join([e.strip() for e in ext if e]) if ext else ''
# 	return s


def re_sub(vl):
	return re.sub(r'\[.*\]', '', _uniteList(vl), 1)


def _solSpace(s):
	return s.strip().replace('\t', '').replace('\r', '').replace('\n', '').replace('　----', '').replace('----', '')


def _uniteList(vl):
	vl_1 = ''.join([_solSpace(v) for v in vl if v]) if vl else ''
	return vl_1
