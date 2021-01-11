from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_demo.scrapy_demo.spiders.extract import ExtractSpider
import os, sys
import argparse

BASE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "result")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('urls', nargs='+',
                    help='start urls to crawl')
	parser.add_argument('-t', '--text', nargs='*', default=[".pdf"],
                    help='text file extensions (.pdf, .doc, .docx, .txt, .csv, ...)')
	parser.add_argument('-i', '--img', nargs='*', default=[],
                    help='image file extensions (.jpg, .png, .jpeg, .gif, .svg, ...)')
	parser.add_argument("-d", "--depth", default=1, type=int, help='crawling depth')
	parser.add_argument("-o", "--output", default=BASE_DIR, help='output directory')
	args = parser.parse_args()
	# print(vars(args))

	settings = get_project_settings()
	settings.update({
		'DEPTH_LIMIT': args.depth,
		'DOWNLOAD_DELAY': 1,
		'ROBOTSTXT_OBEY': True,
	})
	process = CrawlerProcess(settings)
	process.crawl(ExtractSpider, **vars(args))
	process.start()

