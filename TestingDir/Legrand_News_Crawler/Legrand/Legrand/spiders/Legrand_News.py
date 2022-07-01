from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import datetime
import dateparser
import datefinder
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class LegrandNewsSpider(CrawlSpider):
    name = 'Legrand_News'
    
    allowed_domains = ['legrandgroup.com' , 'legrand.us']
    start_urls = [
        'https://www.legrandgroup.com/en/press/newsroom',
        'https://www.legrand.us/press?q=%3ApublishingDate-desc&page=0&&pageSize=90'
    ]
    BASE_URL = "https://www.legrandgroup.com"
    rules = (
        Rule(LinkExtractor(restrict_xpaths=["//h2/a", "//div[@class='text']"]), callback='parse_item'),
        Rule(LinkExtractor(restrict_xpaths=["//div[@class='pagination']//a[@rel='next']"]), follow=True),
        Rule(LinkExtractor(restrict_xpaths=["//li[@class='pagination-next']"]), follow=True) 
    )

    def parse_item(self, response):
        filter_link = response.url
        item = {}
        if "legrandgroup.com" in filter_link:
            item['title'] = self.legrand_group_title(response)
            item['Date'] = dateparser.parse(self.legrand_group_news_date(response))
            item['Crawled_On'] = datetime.datetime.now()
            item['Language'] = 'en'
            item['News_Weblink'] = response.url
            item['Image'] = self.legrand_group_imgae(response)
            item['Videos'] = ''
            item['Announcement'] = self.legrand_group_announcement(response)
            item['HistorySubcategory'] = self.legrand_group_sub_category(response)
            item['Analysis'] = self.legrand_group_analysis(response)
            item['Press_Release'] = self.legrand_group_press_release(response)
            item['PageSource'] = self.legrand_group_pagesource(response)
        else:
            item['title'] = self.legrand_us_title(response)
            item['Date'] = dateparser.parse(self.legrand_us_news_date(response))
            item['Crawled_On'] = datetime.datetime.now()
            item['Language'] = 'en'
            item['News_Weblink'] = response.url
            item['Image'] = ''
            item['Videos'] = ''
            item['Announcement'] = self.legrand_us_announcement(response)
            item['HistorySubcategory'] = self.legrand_us_sub_category(response)
            item['Analysis'] = self.legrand_us_analysis(response)
            item['Press_Release'] = ''
            item['PageSource'] = self.legrand_us_pagesource(response)
            
        return item
    
    def legrand_group_title(self, response):
        title = response.xpath("//h2[@itemprop='headline']/text()").get()
        return title

    def legrand_group_analysis(self, response):
        analysis = response.xpath("//meta[@property='og:description']/@content").get()
        return analysis

    def legrand_group_sub_category(self, response):
        sub_category = response.xpath("//h3[@class='type']/text()").get()
        sub_category = sub_category.replace("|","").strip() 
        return sub_category

    def legrand_group_news_date(self, response):
        date = response.xpath("//meta[@itemprop='datePublished']/@content").get()
        return date

    def legrand_group_imgae(self, response):
        image = response.xpath("//div[@class='visuel floating-right']/img/@src").get()
        if image == None:
            return image
        else:
            return self.BASE_URL + image

    def legrand_group_announcement(self, response):
        announcement = response.xpath("//div[@class='wysiwyg']//p/text()").getall()
        return announcement
    
    def legrand_group_press_release(self, response):
        press_release_document = response.xpath("//a[@class='dl']/@href").get()
        if press_release_document == None:
            return press_release_document
        else:
            return  self.BASE_URL + press_release_document
    
    def legrand_group_pagesource(self, response):
        page_source = "https://www.legrandgroup.com/en/press/newsroom"
        return page_source

# *******************************************************************************

    def legrand_us_title(self, response):
        title = response.xpath("//h1/text()").get()
        return title

    def legrand_us_analysis(self, response):
        analysis = response.xpath("//meta[@name='description']/@content").get()
        return analysis

    def legrand_us_sub_category(self, response):
        try:
            sub_category = response.xpath("//meta[@property:'og:type']/@content").get()
        except:
            sub_category = ""
        return sub_category
    
    def legrand_us_news_date(self, response):

        for_date = response.xpath("string(//div[@class='yCmsComponent col-xs-12 yComponentWrapper'])").get()
        matches = datefinder.find_dates(for_date)
        date = [x for x in matches]
        if len(date) == 0:
            return date
        else:
            return date[0]
    
    def legrand_us_announcement(self, response):
        announcement = response.xpath("string(//div[@class='yCmsComponent col-xs-12 yComponentWrapper'])").get()
        return announcement
    
    def legrand_us_pagesource(self, response):
        page_source = "https://www.legrand.us/press"
        return page_source

    
if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(LegrandNewsSpider)
    process.start()

    
