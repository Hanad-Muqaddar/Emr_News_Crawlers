import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
import requests

class AbbRdSpider(scrapy.Spider):
    name = 'abb_rd'
    allowed_domains = ['hitachi.com']
    start_urls = ['https://www.hitachi.com/rd/news/index.html']

    def parse(self, response):
        all_rows = response.css(".DateListStyle2")
        for j in all_rows:
            link = j.css(".ResponsiveLinkListStyle a::attr(href)").get()
            if 'http' not in link:
                link = "https://www.hitachi.com" + link
            news_date = j.css('dt ::text').get()
            title = j.css(".ResponsiveLinkListStyle a::text").get()
            # # *******************************
            # res = requests.get(link)
            # result = Selector(res.content)
            # # *******************************
            # announcement = self.parse_announcement(result)


            item = {}
            item['url'] = link
            item['news_date'] = news_date
            item['title'] = title
            # item['announcemet'] = announcement
            yield item
    
    
    
    
    def parse_announcement(self, response):
        announcement = response.css('.TextStyle1 ::text').getall()
        announc = ""
        for j in announcement:
            announc = announc + j
        return announc