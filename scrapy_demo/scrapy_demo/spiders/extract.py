import re
from scrapy.linkextractors import LinkExtractor
import scrapy
from scrapy.http import Request
import os, sys
from pathlib import Path
from urllib.parse import urlparse, urljoin

URL_REGEX = re.compile(
	r'\b((?:(ht|f)tps?:\/\/)'
	r'(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|'
	r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|'
	r'(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?'
	r'(?:\/[\w \.-]*)*\/?)\b' 
	, re.IGNORECASE)
BASE_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent.parent, "result/")

def extract_list(value):
	if isinstance(value, list):
		return value
	return value.replace(" ", "").split(",")

class LinkExtractorCustom(LinkExtractor):

	def __init__(self, allow_ext, *args, **kwargs):
		super(LinkExtractorCustom, self).__init__(*args, **kwargs)

		self.tags = ['a', 'area', 'img']
		self.attrs = ['href', 'src']
		self.deny_extensions = [ext for ext in self.deny_extensions if ext not in allow_ext]

class ExtractSpider(scrapy.Spider):
	name = "extractor"
	# start_urls = [
	# 	'https://www.imagescape.com/media/uploads/zinnia/2018/08/20/scrape_me.html',
	# 	'https://truyentranhaudio.online/manga-slug/dua-mami-ve-nha/',
	# 	'https://truyentranhaudio.online/manga-slug/toi-tu-dong-san-mot-minh/chap-86/',
	# 	'https://www.daimler.com/investors/reports-news/annual-reports/',
	# 	'http://truyenqq.com/truyen-tranh/tho-ren-huyen-thoai-9311',
	# 	'http://truyenqq.com/truyen-tranh/vua-choi-da-co-tai-khoan-vuong-gia-10552',
	# 	'http://truyenqq.com/truyen-tranh/toi-la-tho-san-co-ki-nang-tu-sat-cap-sss-10675',
	# 	'https://vingroup.net/quan-he-co-dong/bao-cao-tai-chinh/2020',
	# 	'http://www.nettruyen.com/truyen-tranh/tri-tue-nhan-tao-36737',
	# 	'https://www.coolfreecv.com/',
	# 	'https://www.resumeviking.com/templates/word/',
	# ]

	# custom_settings = {
	# 	'DEPTH_LIMIT': 1,
	# 	'DOWNLOAD_DELAY': 1,
	# }

	def __init__(self, *args, **kwargs):
		super(ExtractSpider, self).__init__(*args, **kwargs)
		self.start_urls = extract_list(kwargs.get("urls", []))
		self.txt_extensions = extract_list(kwargs.get("text", [".pdf"]))
		self.img_extensions = extract_list(kwargs.get("img", []))

		self.output_dir = kwargs.get("output", BASE_DIR)
		# print(kwargs)

		self.link_extractor = LinkExtractorCustom(self.txt_extensions + self.img_extensions)

	def parse(self, response, **kwargs):
		print("URL:", response.url, "\n\n")
		if hasattr(response, "text"): # HTML page
			# Extract links in HTML page	
			for link in self.link_extractor.extract_links(response):
				# print(link)
				yield Request(
					response.urljoin(link.url), 
					callback=self.parse,
					cb_kwargs=dict(prev_url=response.url)
				)

			# Extract image links in img tag
			if self.img_extensions:	
				for src in response.css("img::attr(src)").extract():
					# print(src)
					yield Request(
						url=response.urljoin(src),
						callback=self.parse,
						cb_kwargs=dict(prev_url=response.url)
					)

			# Extract links in script tag	
			for script in response.css("script::text").extract():
				for url in re.findall(URL_REGEX, script):
					# print(url[0])
					yield Request(
					response.urljoin(url[0]), 
					callback=self.parse,
					cb_kwargs=dict(prev_url=response.url)
					)
		else:
			self.parse_item(response, **kwargs)

	def parse_item(self, response, **kwargs):
		url = response.url.split("?")[0]                                                                                                          
		check_txt = next(filter(lambda x: url.lower().endswith(x), self.txt_extensions), False)
		check_img = next(filter(lambda x: url.lower().endswith(x), self.img_extensions), False)

		if check_txt or check_img:
			prev_url = kwargs.get('prev_url', None)
			if prev_url:
				result = urlparse(prev_url)
				directory = result.path[1:].split(".")[0]
				output_dir = os.path.join(self.output_dir, directory)
			else:
				output_dir = self.output_dir

			if not os.path.exists(output_dir):
				os.makedirs(output_dir)

			path = os.path.join(output_dir, url.split('/')[-1])

			self.logger.info('Saving file to %s', path)
			with open(path, 'wb') as f:
				f.write(response.body)
