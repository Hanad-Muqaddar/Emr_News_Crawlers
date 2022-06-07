from pymongo import database
import scrapy
from scrapy_selenium import SeleniumRequest
import datetime
import dateparser
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class WescManualSpider(scrapy.Spider):
    name = 'Wesc_Manual'
    allowed_domains = ['investors.wesco.com']
    def start_requests(self):
        url = "https://investors.wesco.com/news-and-events/news-releases/default.aspx?l=100&o=0"
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        for link in response.css(".module_item a::attr(href)").getall():
            yield response.follow(url=link, callback=self.parse_links)
    
    def parse_links(self, response):
        item = {}
        item['Date'] = self.parse_date(response)
        item['Source'] = "https://investors.wesco.com/news-and-events/news-releases/default.aspx?l=100&o=0"
        item['historySubCategory'] = ""
        item['News_Weblink'] = response.url
        item['announcement'] = self.parse_announcement(response)
        item['companyId'] = ""
        item['location'] = ""
        item['comment'] = ""
        item['title'] = self.parse_title(response)
        item['announcementType'] = 'News Releases'
        item['photo'] = ""
        item['Language'] = 'English'
        item['Crawled_on'] = datetime.datetime.now()
        return item
    
    def parse_title(self, response):
        title = response.css("#_ctrl0_ctl54_lblModuleDetailHeadline ::text").get()
        return title
    
    def parse_date(self, response):
        news_date = response.css(".module_date-text ::text").get()
        return dateparser.parse(news_date)
    
    def parse_announcement(self, response):
        ann = response.css(".module_body p ::text").getall()
        announcement = ""
        for j in ann:
            announcement = announcement + j
        return announcement

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(WescManualSpider, domain='investors.wesco.com')
    process.start()
    
