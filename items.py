from scrapy.item import Item, Field


class PageItem(Item):
    url = Field()
    base_url = Field()
    previous_page_id = Field()
    path = Field()
    query = Field()
    status = Field()
    headers = Field()
    cookies = Field()
    body = Field()
    dirbust = Field()
    hash = Field()

    def __str__(self):
        return super(PageItem, self).__str__().replace('\n', '')[:50] + '...'
