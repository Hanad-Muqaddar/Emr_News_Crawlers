import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import datetime

class HoneyWellInthenewsSpider(scrapy.Spider):
    name = 'Honey_Well_InTheNews'
    allowed_domains = ['honeywell.com']
    start_urls = ['https://www.honeywell.com/us/en/in-the-news']


    def parse(self, response):
        for item in response.css(".content-grid-items a"):
            try:
                link = item.css('::attr(href)').get()
                if "http" not in link:
                    link = "https://www.honeywell.com" + link
            except:
                link = ""
            title = item.css(".pt-md-0 ::text").get()
            announcement = item.css("p ::text").get()
            image = item.css("img ::attr(src)").get()

            my_item = {}
            my_item['Date'] = ""
            my_item['announcementType'] = 'News'
            my_item['Source'] = 'https://www.honeywell.com/us/en/in-the-news'
            my_item['News_Weblink'] = link
            my_item['title'] = title
            my_item['photo'] = image
            my_item['announcement'] = announcement
            my_item['Language'] = "English"
            my_item['analysis'] = ""
            my_item['historySubCategory'] = ""
            my_item['Crawled_on'] = datetime.datetime.now()
            yield my_item

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(HoneyWellInthenewsSpider, domain='honeywell.com')
    process.start()