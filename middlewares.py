import logging
import itertools
from urllib.parse import urlparse, urlunparse, urljoin

from scrapy.http import Request
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class PreviousPageMiddleware(object):

    def process_spider_output(self, response, result, spider):
        for r in result:
            if isinstance(r, Request):
                r.meta['previous_page'] = response.url
            yield r

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            r.meta['previous_page'] = None
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
