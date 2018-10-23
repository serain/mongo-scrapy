import re
import pymongo


class MongoPipeline(object):
    collection_name = 'pages'

    def __init__(self, mongo_host, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('MONGO_HOST'), crawler.settings.get('MONGO_DB'))

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_host)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item['body'] = item['body'].decode('utf-8')

        # parse out the headers
        cleaned_headers = []
        for key, value in item['headers'].items():
            cleaned_headers.append({
                'name': key.decode('utf-8').lower(),
                'value': value[0].decode('utf-8')
            })
        
        item['headers'] = cleaned_headers

        # if there's a 'set-cookie' header, parse out the cookies
        for header in item['headers']:
            if header['name'] == 'set-cookie':
                item['cookies'] = self._get_cookies(header['value'])
                break

        self.db[self.collection_name].update({'url': item['url']}, item, upsert=True)

        return item

    def _get_cookies(self, set_cookie):
        # remove 'expires' field of cookies, because they cause problems
        if 'expires=' in set_cookie:
            set_cookie = re.sub(r'expires=.*?; ?', '', set_cookie)

        cookies = []

        for cookie in re.split('(?<![;,0-9]) ', set_cookie):
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value.split(';', 1)[0]
                })
            # modern cookies should have '=', but some legacy ones don't
            else:
                cookies.append({
                    'name': cookie,
                    'value': ''
                })
        
        return cookies
