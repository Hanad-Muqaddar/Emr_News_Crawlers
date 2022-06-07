from dateutil.parser import parse
import scrapy
import datefinder
import datetime
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class SoneparCrawlerSpider(scrapy.Spider):
    name = 'SonePar_Crawler'
    allowed_domains = ['soneparusa.com']
    start_urls = ['https://soneparusa.com/index.html']


    def parse(self, response):
        links = response.xpath('//a[@class="btn btn-primary"]/@href').getall()
        numbers = []
        for j in links:
            numbers.append(j.replace("news","").replace(".html",""))
        int_lst = [int(x) for x in numbers]
        max_number = max(int_lst)
        links_list = []
        for link in range(1,max_number+1):
            links_list.append("https://soneparusa.com/news{}.html".format(link))
        for news_link in links_list:
            yield scrapy.Request(url=news_link, callback=self.news_parser)
    
    def news_parser(self, response):
        item = {}
        item['title'] = self.parse_title(response)
        item['Date'] = self.parse_news_date(response)
        item['Crawled_On'] = datetime.datetime.now()
        item['Language'] = 'en'
        item['News_Weblink'] = response.url
        item['Image'] = self.parse_image(response)
        item['Videos'] = ''
        item['Announcement'] = self.parse_announcement(response)
        item['HistorySubcategory'] = ''
        item['Analysis'] = ''
        item['PageSource'] = self.parse_page_source(response)

        return item

    
    def parse_title(self, response):
        title = response.xpath("//h2/text()").get()
        return title
    
    def parse_announcement(self, response):
        # announcement = response.xpath("string(//div[@class='container blog-content-section'])").get()
        announcement = response.xpath("string(//section[2])").get()
        announcement = re.sub(r'\s+', ' ', announcement)
        return announcement
    
    def parse_news_date(self, response):
        announcement = self.parse_announcement(response)
        matches = datefinder.find_dates(announcement)
        date = [x for x in matches]
        if len(date) == 0:
            return date
        else:
            return date[0]
    
    def parse_image(self, response):
        image = response.xpath("//div[@class='container blog-content-section']//p//img/@src").get()
        try:
            return "https://soneparusa.com/" + image
        except:
            return image
        
    def parse_page_source(self,response):
        page_source = "https://soneparusa.com/"
        return page_source

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(SoneparCrawlerSpider, domain='soneparusa.com')
    process.start()
    

