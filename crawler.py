from scraper import Scraper

scraper = Scraper(depth=1)								# Max crawling depth
scraper.crawl(	
	url_list=["https://www.coolfreecv.com/", 			# Start urls to crawl
	"https://www.resumeviking.com/templates/word/"], 
	txt_extensions=[".docx", ".doc"],					# Text file extensions (.pdf, .docx, ...)
	img_extensions=[".jpg"],							# Image file extensions (.jpg, .png, ...)
	output_dir="D:/scala/"								# Output directory
	)