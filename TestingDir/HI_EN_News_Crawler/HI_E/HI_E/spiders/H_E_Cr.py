from scrapy.spiders import SitemapSpider
import dateparser
import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class MySpider(SitemapSpider):
    name = "Hitachi"
    sitemap_urls = ['https://www.hitachienergy.com/news/sitemap.xml']
    sitemap_rules = [
        ('/news/', 'parse_news'),
    ]

    def parse_news(self, response):
        item = {}
        item['Date'] = self.parse_news_date(response)
        item['Crawled_on'] = datetime.datetime.now()
        item['announcementType'] = 'Press Release'
        item['Source'] = 'https://www.hitachienergy.com/media'
        item['News_Weblink'] = response.url
        item['title'] = self.parse_title(response)
        item['photo'] = ''
        item['announcement'] = self.parse_announcement(response)
        item['Language'] = 'English'
        item['analysis'] = self.parse_analysis(response)
        item['historySubCategory'] = ''
        return item
    
    def parse_news_date(self, response):
        try:
            news_date = response.xpath("//meta[@itemprop='date']/@content").get()
            news_date = str(news_date)
            news_date = dateparser.parse(news_date)
        except:
            news_date = datetime.now()
        return news_date
    
    def parse_title(self, response):
        title = response.css("title ::text").get()
        return title
    
    def parse_announcement(self, response):
        announcement = response.xpath("normalize-space(//div[@class='cmp-text'])").get()
        return announcement
    
    def parse_analysis(self, response):
        analysis = response.xpath('//meta[@name="description"]/@content').get()
        return analysis


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(MySpider)
    process.start()