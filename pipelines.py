import pymongo
import htmlmin


class MongoPipeline(object):
    collection_name = 'pages'

    def __init__(self, mongo_host, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get('MONGO_HOST'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_host)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item['body'] = htmlmin.minify(item['body'].decode('utf-8'))

        self.db[self.collection_name].update({
            'base_url': item['base_url'],
            'path': item['path'],
            'query': item['query']
        }, item, upsert=True)
        return item
