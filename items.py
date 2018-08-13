from scrapy.item import Item, Field


class PageItem(Item):
    base_url = Field()
    path = Field()
    query = Field()
    status = Field()
    headers = Field()
    cookies = Field()
    body = Field()
