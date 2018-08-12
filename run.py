import argparse
from scrapy.crawler import CrawlerProcess

from spider import MongoSpider


def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-iL', '--input-list', required=True,
                        help='list of URLs to crawl')
    # parser.add_argument('--mongo-host', default='127.0.0.1',
    #                     help='mongo host')
    # parser.add_argument('--mongo-db', default='crawler',
    #                     help='mongo database')

    return parser.parse_args()


def main():
    args = get_args()

    with open(args.input_list) as fh:
        urls = fh.read().splitlines()

    for url in urls:
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        })

        process.crawl(MongoSpider, url)
        process.start()

        exit()


if __name__ == '__main__':
    main()
