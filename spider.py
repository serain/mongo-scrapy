import logging
from urllib.parse import urlparse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from items import PageItem
from pipelines import MongoPipeline
from hashes import get_not_found_hashes, get_hash


logger = logging.getLogger(__name__)


class MongoSpider(CrawlSpider):
    name = 'mongo-spider'

    custom_settings = {
        'ITEM_PIPELINES': {
            'pipelines.MongoPipeline': 100
        },
        'SPIDER_MIDDLEWARES': {
            'middlewares.DirbustMiddleware': 300,
            'middlewares.PreviousPageMiddleware': 100,
            'middlewares.SpiderRedirectMiddleware': 1000,
            'middlewares.FilterDirbustItemsMiddleware': 200
        },
        'REDIRECT_ENABLED': False,
        'HTTPERROR_ALLOW_ALL': True
    }

    rules = (
        Rule(LinkExtractor(allow=('', )), callback='parse_page'),
    )

    def __init__(self, start_url,  *args, **kwargs):
        super(MongoSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [urlparse(start_url).netloc]
        self.not_found_hashes = get_not_found_hashes(start_url)

        logger.debug(f'Using the following "Not Found" hashes: {self.not_found_hashes}')

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        parsed_url = urlparse(response.url)

        item = PageItem()
        item['url'] = response.url
        item['base_url'] = self.start_urls[0]
        item['previous_page_id'] = response.meta['previous_page_id']
        item['path'] = parsed_url.path
        item['query'] = parsed_url.query
        item['status'] = response.status
        item['headers'] = response.headers
        item['body'] = response.body
        item['dirbust'] = response.meta['dirbust'] if 'dirbust' in response.meta else False
        item['hash'] = get_hash(response.body.decode())

        return item
