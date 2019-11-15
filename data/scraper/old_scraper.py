import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher

class Scraper(scrapy.Spider):

    name = 'redditbot'
    #allowed_domains = ['www.reddit.com/r/gameofthrones/']
    #start_urls = ['https://en.wikipedia.org/wiki/Web_scraping']
    start_urls = ['http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10638']
    custom_settings = {
        'DEPTH_LIMIT': 1
    }

    def parse(self, response):
        links = response.css("a")[4:]
        for next_page in links:
            yield response.follow(next_page, self.parse)

        for text in response.css('div::text'):
            yield {"text": text.extract()}

def spider_results():
    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_passed)

    process = CrawlerProcess(get_project_settings())
    process.crawl(Scraper)
    process.start()  # the script will block here until the crawling is finished
    return results


if __name__ == '__main__':
    results = [result["text"] for result in spider_results() if "\r\n" not in result["text"]]
    print("".join(results))
