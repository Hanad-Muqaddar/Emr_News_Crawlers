from time import time
from scrapy.spiders import XMLFeedSpider
from scrapy import Request, item
import dateparser
import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class MySpider(XMLFeedSpider):
    name = 'GraingerNews'
    allowed_domains = ['grainger.com']
    start_urls = ['https://pressroom.grainger.com/rss/pressrelease.aspx']
    iterator = 'html'
    itertag = 'item'

    def parse_node(self, response, node):
        link =  node.xpath("text()").get()
        yield Request(url=link, callback=self.parse_news)
    
    def parse_news(self, response):
        item = {}
        item['Date'] = self.parse_date(response)
        item['Crawled_on'] = datetime.datetime.now()
        item['announcementType'] = 'News'
        item['Source'] = 'https://pressroom.grainger.com/news/default.aspx'
        item['News_Weblink'] = response.url
        item['title'] = self.parse_title(response)
        item['photo'] = ''
        item['announcement'] = self.parse_announcement(response)
        item['Language'] = 'English'
        item['analysis'] = self.parse_analysis(response)
        item['historySubCategory'] = ''
        return item
    
    def parse_title(self, response):
        title = response.css("#_ctrl0_ctl66_lblModuleDetailHeadline ::text").get()
        return title
    
    def parse_date(self, response):
        news_date = response.css("#_ctrl0_ctl66_lblDate ::text").get()
        return dateparser.parse(news_date)
    
    def parse_announcement(self, response):
        announcement = response.xpath("normalize-space(//div[@class='xn-content'])").get()
        if announcement == "" or announcement == None:
            announcement = response.xpath("normalize-space(//div[@class='module_body'])").get()
        return announcement
    
    def parse_analysis(self, response):
        analysis = response.xpath("//meta[@property='og:description']/@content").get()
        return analysis

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(MySpider)
    process.start()