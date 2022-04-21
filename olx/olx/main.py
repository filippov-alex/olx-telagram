from scrapy.crawler import CrawlerProcess
from olx.olx.spiders.olxbot import OlxSpider
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(get_project_settings())
process.crawl(OlxSpider)
process.start()