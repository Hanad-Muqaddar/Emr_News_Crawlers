import scrapy
import json
import datetime
import dateparser
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class Test2Spider(scrapy.Spider):
    name = 'Test2'
    allowed_domains = ['osram.com']
    def start_requests(self):
        form_data= {"requests":[{"indexName":"prod_OSRAM_COM_en","params":"query=&hitsPerPage=10&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22content_type_keyword%22%2C%22bu_multi_keyword%22%2C%22dp_year%22%5D&tagFilters=&facetFilters=%5B%5B%22bu_multi_keyword%3AOpto%20Semiconductors%22%5D%2C%5B%22content_type_keyword%3APress%22%5D%5D"},{"indexName":"prod_OSRAM_COM_en","params":"query=&hitsPerPage=1&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=bu_multi_keyword&facetFilters=%5B%5B%22content_type_keyword%3APress%22%5D%5D"},{"indexName":"prod_OSRAM_COM_en","params":"query=&hitsPerPage=1&maxValuesPerFacet=200&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=content_type_keyword&facetFilters=%5B%5B%22bu_multi_keyword%3AOpto%20Semiconductors%22%5D%5D"}]}
        request_body = json.dumps(form_data) 
        url = "https://9ps0m7duie-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.12.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%20(2.28.0)&x-algolia-application-id=9PS0M7DUIE&x-algolia-api-key=321a182fe8706b78ee3234b41c7b58f7"
        yield scrapy.Request(url=url, method="POST", body=request_body, headers={'Content-Type': 'application/json'})

    def parse(self, response):
        data = json.loads(response.body)
        for j in data['results'][0]['hits']:
            news = {}
            news['companyId'] = ""
            news["location"] = ""
            news['Date'] = dateparser.parse(str(j['dp_date']))
            news['title'] = j['title']
            news['announcementType'] = j['dp_category']
            news['announcement'] = j['content']
            news['photo'] = j['src1_picture_stored_only']
            news['Language'] =  'English'
            news['Crawled_on'] = datetime.datetime.now()
            news['Source'] = "https://www.osram.com/os/press/press_overview.jsp"
            news['News_Weblink'] = j['link']
            news['historySubCategory'] = j['dp_subheadline']
            news['analysis'] = j['dp_text']
            yield news
            
if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(Test2Spider)
    process.start()