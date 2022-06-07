import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import dateparser
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import datetime

class HoneywellParserSpider(CrawlSpider):
    name = 'HoneyWell_Parser'
    allowed_domains = ['honeywell.com']
    start_urls = ['https://www.honeywell.com/us/en/press']

    rules = (
        Rule(LinkExtractor(restrict_css='.data-list'), callback='parse_item'),
    )

    def parse_item(self, response):
        if "?tag=" in response.url:
            return
        else:
            item = {}
            item['Date'] = self.parse_date(response)
            item['announcementType'] = 'News'
            item['Source'] = 'https://www.honeywell.com/us/en/press'
            item['News_Weblink'] = response.url
            item['title'] = self.parse_title(response)
            item['photo'] = ""
            item['announcement'] = self.parse_announcement(response)
            item['Language'] = "English"
            item['analysis'] = self.parse_analysis(response)
            item['historySubCategory'] = ""
            item['Crawled_on'] = datetime.datetime.now()
            return item
    
    def parse_title(self, response):
        title = response.css(".old-title ::text").get()
        return title
    
    def parse_date(self, response):
        news_date = response.css(".author-date__time ::text").get()
        try:
            return dateparser.parse(news_date)
        except:
            return news_date
    
    def parse_announcement(self, response):
        announ = response.css(".cmp-text p::text").getall()
        announcement = ""
        for j in announ:
            announcement = announcement + j
        return announcement
    
    def parse_analysis(self, response):
        analysis = response.xpath("//meta[@name='description']/@content").get()
        return analysis

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(HoneywellParserSpider, domain='honeywell.com')
    process.start()