from scrapy.item import Item, Field


class PageItem(Item):
    base_url = Field()
    path = Field()
    query = Field()
    status = Field()
    headers = Field()
    cookies = Field()
    body = Field()

    def __str__(self):
        return super(PageItem, self).__str__().replace('\n', '')[:50] + '...'
