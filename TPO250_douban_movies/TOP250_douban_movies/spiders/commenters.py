# -*- coding: utf-8 -*-
import datetime
import re
import time
import pymongo
import scrapy
from scrapy import Request

from TOP250_douban_movies.items import CommenterInfoItem
from TOP250_douban_movies.settings import *


class CommentersSpider(scrapy.Spider):
    name = 'commenters'
    allowed_domains = ['douban.com/people/']
    start_urls = ['http://www.douban.com/people/']

    def start_requests(self):
        commenter_link_list = self.get_commenter_link_list()
        crawled_commenter_link_list = self.get_crawled_commenter_link_list()

        for commenter_link in commenter_link_list:
            # time.sleep(4)
            # self.logger.info(commenter_link)
            # yield Request(url=commenter_link, callback=self.parse_commenters)
            if commenter_link not in crawled_commenter_link_list:
                crawled_commenter_link_list.append(commenter_link)
                time.sleep(4)
                self.logger.info(commenter_link)
                yield Request(url=commenter_link, callback=self.parse_commenters)

    def parse_commenters(self, response):
        commenter_info_item = CommenterInfoItem()

        commenter_link = response.xpath('//*[@id="db-usr-profile"]/div[2]/ul/li[1]/a/@href').extract()
        try:
            commenter_link = commenter_link[0]
        except IndexError:
            # 已经注销账号的用户会出错
            self.logger.info('该用户已经主动注销帐号')
            return

        commenter_info_item['commenter_link'] = commenter_link

        location = response.xpath('//*[@id="profile"]/div/div[2]/div[1]/div/a/text()').extract()
        if location is None:
            lcoation = '未知'
        else:
            try:
                location = location[0]
            except IndexError:
                lcoation = '未知'
        commenter_info_item['location'] = location

        register_timestamp = response.xpath('//*[@id="profile"]/div/div[2]/div[1]/div/div/text()[2]').extract()
        try:
            register_timestamp = register_timestamp[0]
            # 截取 xxxx-xx-xx 日期
            result = re.findall('(.*)加入', register_timestamp)
            register_timestamp = result[0]
            register_timestamp = register_timestamp[0:10]
        except IndexError:
            # 因为有的账号根据log查看后发现是被永久停用的，没法获取注册时间
            register_timestamp = datetime.date.today()

        commenter_info_item['register_timestamp'] = register_timestamp

        account_name = response.xpath('//*[@id="profile"]/div/div[2]/div[1]/div/div/text()[1]').extract()
        account_name = account_name[0]
        account_name = str.strip(account_name)
        commenter_info_item['account_name'] = account_name[0]

        following_num = response.xpath('//*[@id="friend"]/h2/span/a/text()').extract()
        try:
            following_num = following_num[0]
        except IndexError:
            # 如果没有关注的人的话没有用户关注多少人，但会有被0人关注
            following_num = 0
        # 截取 成员xxx 中的数字
        commenter_info_item['following_num'] = following_num[2:]

        follower_num = response.xpath('//*[@id="content"]/div/div[2]/p[1]/a/text()').extract()
        follower_num = follower_num[0]
        result = re.findall("被(.*)人关注", follower_num)
        follower_num = result[0]
        commenter_info_item['follower_num'] = follower_num
        self.logger.info(commenter_info_item)
        yield commenter_info_item

    def get_commenter_link_list(self):
        client = pymongo.MongoClient(host=MONGO_URI, port=27017)
        db = client[MONGO_DATABASE]
        comment_infos_collection = db['comment_infos']
        commenter_link_list = []
        for comment_infos in comment_infos_collection.find():
            commenter_link = comment_infos['commenter_link']
            commenter_link_list.append(commenter_link)
        return commenter_link_list

    def get_crawled_commenter_link_list(self):
        client = pymongo.MongoClient(host=MONGO_URI, port=27017)
        db = client[MONGO_DATABASE]
        commenter_infos_collection = db['commenter_infos']
        crawled_commenter_link_list = []
        for commenter_infos in commenter_infos_collection.find():
            commenter_link = commenter_infos['commenter_link']
            crawled_commenter_link_list.append(commenter_link)
        return crawled_commenter_link_list
