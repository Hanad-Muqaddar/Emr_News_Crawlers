import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import datetime
import dateparser
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class OboSpider(CrawlSpider):
    name = 'OBO'
    allowed_domains = ['obo.global']
    start_urls = ['https://www.obo.global/company/press-releases/', "https://www.obo.global/company/news/"]

    rules = (
        Rule(LinkExtractor(restrict_css=['.teaser--horizontal']), callback='parse_item'),
    )

    def parse_item(self, response):
        item = {}
        item['companyId'] = ''
        item['location'] = ''
        item['comment'] = ''
        item['Date'] = self.parse_date(response)
        item['Crawled_on'] = datetime.datetime.now()
        item['title'] = self.parse_title(response)
        item['Language'] = 'en'
        item['announcementType'] = self.parse_announcement_type(response) 
        item['News_Weblink'] = response.url
        item['photo'] = self.parse_image(response)
        item['videos'] = ''
        item['announcement'] = self.parse_announcement(response)
        item['analysis'] = ""
        item['historySubCategory'] = ""
        return item

    def parse_date(self, response):
        date = dateparser.parse(response.css("time ::text").get(), settings={'DATE_ORDER': 'DMY'})
        return date
    
    def parse_announcement_type(self, response):
        if "/company/press-releases/" in response.url:
            return "Press Release"
        else:
            return "News"

    def parse_title(self, response):
        title = self.clean(response.css("h1 ::text").get())
        return title
    
    def parse_image(self, response):
        image = response.css(".page-content img::attr(src)").get()
        return image
    
    def parse_announcement(self, response):
        announcement = self.clean(response.xpath("normalize-space(//div[@class='news news-single'])").get())
        return announcement

    def _sanitize(self, input_val):
        pattern_re = r'\s+'
        repl_re = ' '
        return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


    def clean(self, lst_or_str):
        if not isinstance(lst_or_str, str) and getattr(
            lst_or_str, '__iter__', False
        ):  # if iterable and not a string like
            return [x for x in (self._sanitize(y) for y in lst_or_str if y is not None) if x]
        return self._sanitize(lst_or_str) if lst_or_str else None

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(OboSpider)
    process.start()