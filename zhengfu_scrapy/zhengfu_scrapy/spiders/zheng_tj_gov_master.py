# -*- coding: utf-8 -*-
import scrapy, re, math
from scrapy.selector import Selector
from util.info import startup_nodes
from rediscluster import StrictRedisCluster


class TouzishijianSpider(scrapy.Spider):
	name = 'tj_gov_master'
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
		f_cla_list = [
			'机构职能', '市政府文件', '政府规章文件', '规划信息', '统计信息',
			'政府工作报告', '财政报告', '行政收费', '政府采购', '行政许可',
			'重大建设项目', '教育医疗', '社保就业', '民政助残扶贫', '突发事件处置',
			'食品药品监管', '产品质量监管', '安全生产监管', '环保公共卫生', '人事任免',
			'其他服务事项', '其他公开信息', '信息公开年度报告'
		]
		t_cla_list = [
			['基本信息', '主要职责', '领导信息', '内设机构', '下属单位'],
			['津政令', '津政发', '津政办发', '津政人', '津政办函'],
			['经贸 商务', '国资 投资', '规划 统计', '工业 信息化', '科技 知识产权', '工商 市场 物价', '财政 税收', '交通 邮政 通信', '金融 证券 期货', '房屋 土地 城建',
			 '市容 绿化', '市政 水利 供水', '农林 畜牧 渔业', '文化 体育 旅游', '广电 影视 出版', '民族 宗教 侨务', '国防 公安 司法', '监察 审计 法制', '人事 档案 表彰',
			 '其他服务管理'],
			['发展规划', '专项规划'],
			['年度公报', '月度信息'],
			['政府工作报告'],
			['年度预算', '年度决算'],
			['行政收费'],
			['政府采购'],
			['行政许可事项'],
			['立项批准', '建设实施'],
			['教育', '医疗卫生'],
			['社保就业'],
			['民政助残扶贫'],
			['突发事件处置'],
			['食品药品监管'],
			['产品质量监管'],
			['产品质量监管'],
			['环保公共卫生'],
			['人事任免'],
			['其他服务事项'],
			['其他公开信息'],
			['信息公开年度报告']
		]
		num_list = [
			[200, 201, 202, 203, 204],
			[205, 206, 207, 281, 283],
			[208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227],
			[228, 229],
			[230, 231],
			[232],
			[233, 234],
			[235],
			[236],
			[237],
			[240, 241],
			[242, 243],
			[245],
			[246],
			[247],
			[182],
			[185],
			[187],
			[189],
			[193],
			[195],
			[197],
			[250]
		]
		num_all = []
		t_cla_all = []
		for i in range(len(t_cla_list)):
			num_all = num_all + num_list[i]
			t_cla_all = t_cla_all + t_cla_list[i]
		t_cla_len = [len(t) for t in t_cla_list]
		t_len_sum = [sum(t_cla_len[:i + 1]) for i in range(len(t_cla_len))]
		burl = 'http://gk.tj.gov.cn/govsearch/search.jsp?page=1&ztfl={}'
		for j, num in enumerate(num_all):
			f_cla = ''
			for i in range(len(t_cla_len)):
				if j < t_len_sum[i]:
					f_cla = f_cla_list[i]
					break
			t_cla = t_cla_all[j]
			url = burl.format(num)
			yield scrapy.Request(url, meta={'f_cla': f_cla, 't_cla': t_cla})

	def parse(self, response):
		f_cla = response.meta.get('f_cla')
		t_cla = response.meta.get('t_cla')
		select = Selector(text=response.text)
		li_tags = select.xpath('//div[@class="index_right_content"]/ul/li')
		for li in li_tags:
			detail_url = li.xpath('./a/@href').extract_first()
			val = f_cla + '~' + t_cla + '~' + detail_url
			self.rc.sadd('zheng_tj_url', val)
		arts = re.findall(r'var m_nRecordCount = (\d+?);', response.text)[0]
		p_num = math.ceil(int(arts) / 10)
		if int(p_num) < 2:
			return
		url = response.url
		now_page = re.search(r'page=(\d+)', url).group(1)
		if int(now_page) >= p_num:
			return
		n_url = re.sub(r'page=\d+', 'page=' + str(int(now_page) + 1), url)
		yield scrapy.Request(n_url, meta={'f_cla': f_cla, 't_cla': t_cla})
