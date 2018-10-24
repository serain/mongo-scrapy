import logging
import itertools
from urllib.parse import urlparse, urlunparse, urljoin

import pymongo
from w3lib.url import safe_url_string

from scrapy.http import Request
from scrapy.signals import spider_opened, spider_closed
from scrapy.exceptions import NotConfigured
from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware

logger = logging.getLogger(__name__)


class SpiderRedirectMiddleware(BaseRedirectMiddleware):
    """
    Create redirect requests from Spider middleware instead of Downloader
    middleware. Allows spidering the redirects and creating items to store
    redirect responses.
    """

    def __init__(self, settings):
        # redefined to exclude REDIRECT_ENABLED check (base class)
        self.max_redirect_times = settings.getint('REDIRECT_MAX_TIMES')
        self.priority_adjust = settings.getint('REDIRECT_PRIORITY_ADJUST')

    def process_spider_output(self, response, result, spider):
        for r in result:
            yield r

        allowed_status = (301, 302, 303, 307, 308)
        if 'Location' not in response.headers or response.status not in allowed_status:
            return

        location = safe_url_string(response.headers['location'])

        redirected_url = urljoin(response.request.url, location)

        if response.status in (301, 307, 308) or response.request.method == 'HEAD':
            redirected = response.request.replace(url=redirected_url)
            yield self._redirect(redirected, response.request, spider, response.status)

        redirected = self._redirect_request_using_get(response.request, redirected_url)
        yield self._redirect(redirected, response.request, spider, response.status)


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
        prev_page = self.db[self.collection_name].find_one({'url': response.url})
        prev_page_id = prev_page['_id'] if prev_page else None
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
        for r in result:
            if isinstance(r, Request):
                for dirb_req in self._generate_dirbust_requests(r.url):
                    yield dirb_req
            yield r

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            for dirb_req in self._generate_dirbust_requests(r.url):
                yield dirb_req
        yield r
    
    def _generate_dirbust_requests(self, url):
        def _get_base_urls(url):
            parsed = urlparse(url)
            dirs = parsed.path.split('/')[1:]
            
            for x in range(0, len(dirs)):
                # append a '/' otherwise urljoin will ignore the last path segment
                # nb: by default none of these will end with '/' due to behavior of split() and join()
                yield f'{urlunparse((parsed.scheme, parsed.netloc, "/".join(dirs[:x]), (), (), ()))}/'

        for base_url in _get_base_urls(url):
            if base_url in self.dirbusted:
                logger.debug(f'Ignoring base URL {base_url} as it\'s already been dirbusted')
                continue
            logger.debug(f'Dirbusting base URL {base_url}')
            self.dirbusted.add(base_url)
            with open(self.dirbust_list) as fh:
                for line in fh:
                    yield Request(urljoin(base_url, line.strip()))
