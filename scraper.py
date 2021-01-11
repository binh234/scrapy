from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_demo.scrapy_demo.spiders.extract import ExtractSpider
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "result")

class Scraper:
    def __init__(self, depth=1):
        # settings_file_path = 'scrapy_demo.scrapy_demo.settings' # The path seen from root, ie. from main.py
        # os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.settings = get_project_settings()
        self.settings.update({
			'DEPTH_LIMIT': depth,
			'DOWNLOAD_DELAY': 1,
			'ROBOTSTXT_OBEY': True,
        })
        self.process = CrawlerProcess(self.settings)
        self.spider = ExtractSpider # The spider you want to crawl

    def crawl(self, url_list, txt_extensions=[".pdf"], img_extensions=[], output_dir=BASE_DIR):
        self.process.crawl(self.spider, urls=url_list, text=txt_extensions, img=img_extensions, 
        	output=output_dir)
        self.process.start()  # the script will block here until the crawling is finished