# -*- coding: utf-8 -*-
import random
import re
import time
import pyquery as pq
import pymongo
import scrapy
from scrapy import Request

from TOP250_douban_movies.items import CommenterInfoItem


class CommentersSpider(scrapy.Spider):
    name = 'commenters'
    allowed_domains = ['douban.com/people/']
    start_urls = ['http://www.douban.com/people/']

    def start_requests(self):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client['top_250_douban_movies']
        comment_infos_collection = db['comment_infos']
        commenter_link_list = []
        for comment_infos in comment_infos_collection.find():
            commenter_link = comment_infos['commenter_link']
            commenter_link_list.append(commenter_link)

        for index in range(250):
            if index >= 250:
                break
            commenter_link = commenter_link_list[index]
            time.sleep(3)
            self.logger.info(commenter_link)
            yield Request(url=commenter_link, callback=self.parse_comments)

    def parse_commenters(self, response):
        commenter_info_item = CommenterInfoItem()
        html = response.text
        doc = pq(html)

        location = doc('#profile > div > div.bd > div.basic-info > div > a')
        following_num = doc('#friend > h2 > span > a')
        follower_num = doc('#content > div > div.aside > p.rev-link > a')


        # commenter_info_item['commenter'] = commenter
        # commenter_info_item['commenter_link'] = commenter_link
        # commenter_info_item['brief_comment'] = brief_comment
        # commenter_info_item['comment_useful_upvote'] = comment_useful_upvote
        # commenter_info_item['comment_timestamp'] = comment_timestamp
        # commenter_info_item['comment_rating_stars'] = comment_rating_stars
        # commenter_info_item['comment_movie_title'] = comment_movie_title

        self.logger.info(commenter_info_item)
        yield commenter_info_item
