import logging
import itertools
from urllib.parse import urlparse, urlunparse, urljoin

import pymongo
from scrapy.http import Request
from scrapy.signals import spider_opened, spider_closed
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class PreviousPageMiddleware(object):
    collection_name = 'pages'

    def __init__(self, mongo_host, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings.get('MONGO_HOST'), crawler.settings.get('MONGO_DB'))
        crawler.signals.connect(obj.open_spider, signal=spider_opened)
        crawler.signals.connect(obj.close_spider, signal=spider_closed)
        return obj

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_host)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_spider_output(self, response, result, spider):
        prev_page_id = self.db[self.collection_name].find_one({'url': response.url})['_id']
        for r in result:
            if isinstance(r, Request):
                r.meta['previous_page_id'] = prev_page_id
            yield r

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            r.meta['previous_page_id'] = None
        yield r


class DirbustMiddleware(object):

    def __init__(self, dirbust_list):
        self.dirbusted = set()
        self.dirbust_list = dirbust_list

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('DIRBUST_ENABLED'):
            raise NotConfigured
        obj = cls(crawler.settings.get('DIRBUST_LIST'))
        return obj

    def process_spider_output(self, response, result, spider):
        def _get_base_urls(url):
            parsed = urlparse(url)
            dirs = parsed.path.split('/')[1:]
            
            for x in range(0, len(dirs)):
                # append a '/' otherwise urljoin will ignore the last path segment
                # nb: by default none of these will end with '/' due to behavior of split() and join()
                yield f'{urlunparse((parsed.scheme, parsed.netloc, "/".join(dirs[:x]), (), (), ()))}/'

        for r in result:
            if isinstance(r, Request):
                for base_url in _get_base_urls(r.url):
                    if base_url in self.dirbusted:
                        logger.debug(f'Ignoring base URL {base_url} as it\'s already been dirbusted')
                        continue
                    logger.debug(f'Dirbusting base URL {base_url}')
                    self.dirbusted.add(base_url)
                    with open(self.dirbust_list) as fh:
                        for line in fh:
                            yield Request(urljoin(base_url, line.strip()))
            yield r
