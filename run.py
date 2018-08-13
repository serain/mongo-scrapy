import argparse
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from spider import MongoSpider


def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-iL', '--input-list', required=True,
                        help='list of URLs to crawl')
    parser.add_argument('--mongo-host', default='127.0.0.1',
                        help='mongo host')
    parser.add_argument('--mongo-db', default='crawler',
                        help='mongo database')

    return parser.parse_args()


def main():
    args = get_args()

    with open(args.input_list) as fh:
        urls = fh.read().splitlines()

    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    runner = CrawlerRunner({
                'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
                'MONGO_HOST': args.mongo_host,
                'MONGO_DB': args.mongo_db,
                'DEPTH_LIMIT': 4
             })


    @inlineCallbacks
    def loop_urls(urls):
        for url in urls:
            yield runner.crawl(MongoSpider, url)
        reactor.stop()

    loop_urls(urls)
    reactor.run()


if __name__ == '__main__':
    main()
