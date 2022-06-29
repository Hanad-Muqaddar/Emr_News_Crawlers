from os import name
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import datetime
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import dateparser 

class AbbSpider(CrawlSpider):
    name = 'abb'
    allowed_domains = ['hitachi.com']
    start_urls = ['https://www.hitachi.com/New/cnews/index.html','https://www.hitachi.com/rd/news/index.html']

    rules = (
        Rule(LinkExtractor(restrict_css=['.BackNumber']), follow=True),
        Rule(LinkExtractor(restrict_css=['.DateListStyle2']), callback='parse_item'),
    )

    def parse_item(self, response):
        if '2022' in response.url:
            if '/rd/' in response.url:
                item = {}
                item['companyId'] = ''
                item['location'] = ''
                item['comment'] = ''
                item['Date'] = self.parse_date(response)
                item['Crawled_on'] = datetime.datetime.now()
                item['title'] = self.parse_rd_title(response)
                item['Language'] = 'en'
                item['announcementType'] = 'News & Events' 
                item['Source'] = 'https://www.hitachi.com/rd/news/index.html'
                item['News_Weblink'] = response.url
                item['photo'] = self.parse_rd_image(response)
                item['videos'] = ''
                item['announcement'] = self.parse_announcement(response)
                item['analysis'] = self.parse_analysis(response)
                item['historySubCategory'] = 'News & Events'
                return item
            else:
                item = {}
                item['companyId'] = ''
                item['location'] = ''
                item['comment'] = ''
                item['Date'] = self.parse_date(response)
                item['Crawled_on'] = datetime.datetime.now()
                item['title'] = self.parse_title(response)
                item['Language'] = 'en'
                item['announcementType'] = 'News Release' 
                item['Source'] = 'https://www.hitachi.com/New/cnews/index.html'
                item['News_Weblink'] = response.url
                item['photo'] = ''
                item['videos'] = ''
                item['announcement'] = self.parse_announcement(response)
                item['analysis'] = self.parse_analysis(response)
                item['historySubCategory'] = 'News Release'
                return item
        
    def parse_date(self, response):
        news_date = response.css(".RightAdjust ::text").get()
        if news_date == '' or news_date == None or news_date == 'null':
            news_date = response.css(".RdNewsreleaseText ::text").get()
        return dateparser.parse(news_date)
    
    def parse_title(self, response):
        title = response.css(".note1 ::text").get()
        if title == '' or title == None or title == 'null':
            title = response.css('.Section h2 span ::text').get()
        if title == '' or title == None or title == 'null':
            title = response.css('.Section h3 span ::text').get()
        return title
    
    def parse_announcement(self, response):
        announcement = response.css('.TextStyle1 ::text').getall()
        announc = ""
        for j in announcement:
            announc = announc + j
        # if announc == '' or announc == None or announc == 'null':
        #     announc = clean(response.css(".RdNewsreleaseText ::text").getall())
        #     for j in announc:
        #         announc = announc + j
        return announc
    
    def parse_analysis(self, response):
        analysis = response.xpath("//meta[@name='description']/content").get()
        return analysis
    
    def parse_rd_title(self, response):
        title = response.xpath("//a[@id='body']/text()").get()
        return title
    
    def parse_rd_image(self, response):
        image = response.xpath("//meta[@property='og:image']/content").get()
        return image
    
    


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(AbbSpider)
    process.start()