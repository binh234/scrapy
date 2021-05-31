from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_demo.scrapy_demo.spiders.extract import ExtractSpider
import os

class Scraper:
    def __init__(self, log_path, depth=1):
        settings_file_path = 'scrapy_demo.scrapy_demo.settings' # The path seen from root, ie. from main.py
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.settings = get_project_settings()
        self.settings.update({
			'DEPTH_LIMIT': depth,
			'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 0.5,
            'FEED_URI': log_path
        })
        self.process = CrawlerProcess(self.settings)
        self.spider = ExtractSpider # The spider you want to crawl

    def crawl(self, url_list, extensions=[".pdf"], output_dir=None):
        self.process.crawl(self.spider, urls=url_list, ext=extensions, 
        	output=output_dir)
        self.process.start()  # the script will block here until the crawling is finished