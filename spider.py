from urllib.parse import urlparse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from items import PageItem
from pipelines import MongoPipeline


class MongoSpider(CrawlSpider):
    name = 'mongo-spider'

    custom_settings = {
        'ITEM_PIPELINES': {
            'pipelines.MongoPipeline': 100
        }
    }

    rules = (
        Rule(LinkExtractor(allow=('', )), callback='parse_page'),
    )

    def __init__(self, start_url,  *args, **kwargs):
        super(MongoSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [urlparse(start_url).netloc]

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        parsed_url = urlparse(response.url)

        item = PageItem()
        item['base_url'] = self.start_urls[0]
        item['path'] = parsed_url.path
        item['query'] = parsed_url.query
        item['status'] = response.status
        item['headers'] = response.headers
        item['body'] = response.body

        return item
