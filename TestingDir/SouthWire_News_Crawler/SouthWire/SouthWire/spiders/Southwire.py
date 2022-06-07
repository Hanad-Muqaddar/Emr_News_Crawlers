import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import datetime
import dateparser
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class SouthwireSpider(CrawlSpider):
    name = 'Southwire'
    allowed_domains = ['southwire.com']
    start_urls = ['https://www.southwire.com/newsroom']

    rules = (
        Rule(LinkExtractor(restrict_css=".text-dark"), callback='parse_item'),
    )

    def parse_item(self, response):
        item = {}
        item['Date'] = self.parse_news_date(response)
        item['Crawled_on'] = datetime.datetime.now()
        item['announcementType'] = 'News'
        item['Source'] = 'https://www.southwire.com/newsroom'
        item['title'] = self.parse_title(response)
        item['News_Weblink'] = response.url
        item['photo'] = self.parse_image(response)
        item['announcement'] = ''
        item['Language'] = 'English'
        item['analysis'] = ''
        item['historySubCategory'] = ''
        return item

    def parse_title(self, response):
        title = response.css(".mb-4 ::text").get()
        return title
    
    def parse_news_date(self, response):
        news_date = response.css(".article-publishDate-content p::text").get()
        try:
            date = dateparser.parse(news_date)
        except:
            date = news_date
        return date
    
    def parse_image(self, response):
        try:
            image = "https://www.southwire.com" + response.css(".SouthwireArticleSingleImageComponent img ::attr(src)").get()
        except:
            image = ""
        return image

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(SouthwireSpider)
    process.start()