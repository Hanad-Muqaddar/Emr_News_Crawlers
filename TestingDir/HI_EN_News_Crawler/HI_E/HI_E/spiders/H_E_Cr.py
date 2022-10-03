from scrapy.spiders import SitemapSpider
import dateparser
import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import unicodedata
import requests
import json
from pymongo import MongoClient


class MySpider(SitemapSpider):
    
    client = MongoClient("mongodb://su-du-ad:updatedSuperDuperAdmin@18.156.208.71:27017/emrweb?authSource=admin")
    result = client["TEMP_EMR_NEWS_Crawler_DB"]["HITACHI_ABB"].aggregate([
            {
                '$project': {
                    'News_Weblink': 1
                }
            }
        ])
    all_news_links = [i['News_Weblink'] for i in list(result)]
    
    name = "Hitachi"
    sitemap_urls = ['https://www.hitachienergy.com/news/sitemap.xml']
    sitemap_rules = [
        ('/news/press-releases/', 'parse_news'),
    ]

    def parse_news(self, response):
        if response.url in self.all_news_links:
            return
        else:
            item = {}
            item['Date'] = self.parse_news_date(response)
            item['Crawled_on'] = datetime.datetime.now()
            item['announcementType'] = 'Press Release'
            item['Source'] = 'https://www.hitachienergy.com/media'
            item['News_Weblink'] = response.url
            item['title'] = self.parse_title(response)
            try:
                item['photo'] = response.css(".cmp-container--full-width picture img::attr(href)").get()
            except:
                item['photo'] = ""
            announcement , emr_essentail, emr_lite, emr_executive, emr_html = self.parse_announcement(response)
            item['announcement'] = announcement
            item['Language'] = 'English'
            item['analysis'] = self.parse_analysis(response)
            item['historySubCategory'] = ''
            item['emrExecutive'] = emr_executive
            item['emrEssential'] = emr_essentail
            item['emrLite'] = emr_lite
            item['News_Html'] = emr_html
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
    
    def parse_filtered_news(self, announcement):
        api_url = "https://admin.dev.emr-online.com/api/history/filterbody"
        payload = json.dumps({
                                "originalBody": announcement
                                })
        headers = {
                    'Content-Type': 'application/json'
                    }
        return_response = requests.request("POST", api_url, headers=headers, data=payload)
        new_data = return_response.text
        new_data = json.loads(new_data)
        status = new_data['statusCode']
        if status == 200:
            return new_data
        else:
            new_data =  ""
            return new_data

    def parse_announcement(self, response):
        announcement = response.css(".aem-Grid--default--12").get()
        to_replace = response.css(".cmp-pagestage-text-only__heading-container").get()
        to_replace_1 = response.xpath("//div[@data-dm='breadcrumb.component']").get()
        to_replace2 = response.css(".cmp-pagestage-text-only__social-container").get()
        # to_replace_3 = response.css(".cmp-title__text").get()
        try:
            announcement = announcement.replace(to_replace, "")
        except:
            pass
        try:
            announcement = announcement.replace(to_replace_1, "")
        except:
            pass
        try:
            announcement = announcement.replace(to_replace2, "")
        except:
            pass
        return_data = self.parse_filtered_news(announcement)
        try:
            announcement = return_data['filteredBody']
        except:
            announcement = ""
        announcement = unicodedata.normalize("NFKD",announcement)
        try:
            emr_essentail = return_data['emrEssential']
        except:
            emr_essentail = ""
        try:
            emr_executive = return_data['emrExecutive']
        except:
            emr_executive = ""
        try:
            emr_lite = return_data['emrLite']
        except:
            emr_lite = ""
        try:
            emr_html = return_data['emrHtmlText']
        except:
            emr_html = ""
        return announcement , emr_essentail, emr_lite, emr_executive, emr_html
    
    def parse_analysis(self, response):
        analysis = response.xpath('//meta[@name="description"]/@content').get()
        return analysis


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(MySpider)
    process.start()