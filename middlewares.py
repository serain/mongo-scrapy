import logging
import itertools
from urllib.parse import urlparse, urlunparse, urljoin

from scrapy.http import Request

logger = logging.getLogger(__name__)


dirbust_dict = [
    'hello',
    'world',
    'foo',
    'bar'
]


class DirbustMiddleware(object):

    def __init__(self):
        self.dirbusted = set()

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
                    for word in dirbust_dict:
                        yield Request(urljoin(base_url, word))
            yield r
