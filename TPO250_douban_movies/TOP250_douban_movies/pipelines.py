# -*- coding: utf-8 -*-

import pymongo

from TOP250_douban_movies.items import MovieInfoItem, TOP250MovieInfoItem, CommentInfoItem, CommenterInfoItem


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[TOP250MovieInfoItem.collection].create_index([('movie_link', pymongo.ASCENDING)])
        self.db[MovieInfoItem.collection].create_index([('movie_link', pymongo.ASCENDING)])
        self.db[CommentInfoItem.collection].create_index([('commenter_link', pymongo.ASCENDING), ('comment_page_link', pymongo.ASCENDING)])
        self.db[CommenterInfoItem.collection].create_index([('commenter_link', pymongo.ASCENDING)])

    def process_item(self, item, spider):
        if isinstance(item, TOP250MovieInfoItem):
            condition = {'movie_link': item.get('movie_link')}
        elif isinstance(item, MovieInfoItem):
            condition = {'comments_link': item.get('comments_link')}
        elif isinstance(item, CommentInfoItem):
            condition = {'commenter_link': item.get('commenter_link'),
                         'comment_page_link': item.get('comment_page_link')}
        elif isinstance(item, CommenterInfoItem):
            condition = {'commenter_link': item.get('commenter_link')}

        result = self.db[item.collection].find_one(condition)
        if result is None:
            self.db[item.collection].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()