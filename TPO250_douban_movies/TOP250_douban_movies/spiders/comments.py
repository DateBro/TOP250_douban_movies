# -*- coding: utf-8 -*-
import random
import time
import pymongo
import scrapy
from scrapy import Request
from pyquery import PyQuery as pq
import re
from TOP250_douban_movies.items import CommentInfoItem
from TOP250_douban_movies.settings import *


class CommentsSpider(scrapy.Spider):
    name = 'comments'
    allowed_domains = ['movie.douban.com']
    # 用来测试能否爬完一个完整的评论及其后面的评论
    start_urls = ['https://movie.douban.com/subject/1292052/comments?start=0&limit=20&sort=new_score&status=P&percent_type=h']

    def start_requests(self):
        # 每次都要读取这次要开始爬的电影的链接index
        with open('/home/zhiyong/data/next_link_num.txt', 'rt') as f:
            # with open('E:\PycharmProjects\some_data/next_link_num.txt', 'rt') as f:
            next_link_index = f.read()
            next_link_index = int(next_link_index)

        # 将后面开始读的电影索引 + 10 写入文件
        with open('/home/zhiyong/data/next_link_num.txt', 'wt') as f:
            # with open('E:\PycharmProjects\some_data/next_link_num.txt', 'wt') as f:
            new_next_link_index = next_link_index + 10
            f.write(str(new_next_link_index))

        # 后面可以加一个从数据库中读取已爬取的comment链接去重
        movie_link_list = self.get_movie_link_list()
        comment_page_link_list = self.get_comment_page_link_list()

        for index in range(next_link_index, new_next_link_index):
            if index >= 250:
                break
            movie_link = movie_link_list[index]
            time.sleep(3)

            # 分别爬取好评，中评，差评
            choices = ['h', 'm', 'l']
            for choice in choices:
                # 爬取每种评论之前先 sleep 一段时间
                every_type_comments_sleep = random.randint(2, 5)
                time.sleep(every_type_comments_sleep)

                comment_suffix = 'comments?start=$&limit=20&sort=new_score&status=P'
                real_comments_link = movie_link + comment_suffix
                if choice == 'h':
                    real_comments_link = real_comments_link + '&percent_type=h'
                elif choice == 'l':
                    real_comments_link = real_comments_link + '&percent_type=l'
                else:
                    real_comments_link = real_comments_link + '&percent_type=m'

                for start in range(25):
                    tmp_link = real_comments_link
                    request_comments_link = str.replace(tmp_link, '$', str(start * 20))
                    if request_comments_link not in comment_page_link_list:
                        # 然后可以爬取每个 movie 的短评信息
                        self.logger.info(request_comments_link)
                        yield Request(url=request_comments_link, callback=self.parse_comments)
                    else:
                        self.logger.info(request_comments_link)
                        self.logger.info('该链接已经爬取过')

    def parse_comments(self, response):
        comment_page_link = response.url
        self.logger.info('comment_page_link')
        self.logger.info(comment_page_link)
        comment_info_item = CommentInfoItem()
        html = response.text
        doc = pq(html)

        comment_movie_title = doc('#content > h1').text()
        comment_movie_title = comment_movie_title.split(' ')[0]
        comment_items = doc('#comments > div.comment-item')
        for comment_item in comment_items.items():
            commenter = comment_item('div.comment > h3 > span.comment-info > a')
            commenter_link = commenter.attr('href')
            commenter = commenter.text()
            comment_timestamp = comment_item('div.comment > h3 > span.comment-info > span.comment-time').text()
            comment_useful_upvote = comment_item('div.comment > h3 > span.comment-vote > span').text()
            # 处理一下字符串取出分数
            comment_rating_class_value = comment_item(
                "div.comment > h3 > span.comment-info > span:nth-child(3)").attr(
                'class')
            try:
                comment_rating_num = re.search(r"\d+", comment_rating_class_value).group(0)
                comment_rating_stars = int(comment_rating_num) // 10
                brief_comment = comment_item('div.comment > p > span').text()
            except Exception:
                comment_rating_stars = 5
                brief_comment = 'some error happened in get comment_rating_star'
                print(comment_rating_class_value)

            comment_info_item['commenter'] = commenter
            comment_info_item['commenter_link'] = commenter_link
            comment_info_item['brief_comment'] = brief_comment
            comment_info_item['comment_useful_upvote'] = comment_useful_upvote
            comment_info_item['comment_timestamp'] = comment_timestamp
            comment_info_item['comment_rating_stars'] = comment_rating_stars
            comment_info_item['comment_movie_title'] = comment_movie_title
            comment_info_item['comment_page_link'] = comment_page_link

            self.logger.info(comment_info_item)
            yield comment_info_item

    def get_movie_link_list(self):
        client = pymongo.MongoClient(host=MONGO_URI, port=27017)
        db = client[MONGO_DATABASE]
        top_250_movie_infos_collection = db['top_250_movie_infos']
        movie_link_list = []
        for top_250_movie_info in top_250_movie_infos_collection.find():
            movie_link = top_250_movie_info['movie_link']
            movie_link_list.append(movie_link)
        return movie_link_list

    def get_comment_page_link_list(self):
        client = pymongo.MongoClient(host=MONGO_URI, port=27017)
        db = client[MONGO_DATABASE]
        top_250_movie_infos_collection = db['comment_infos']
        comment_page_link_list = []
        for top_250_movie_info in top_250_movie_infos_collection.find():
            comment_page_link = top_250_movie_info['comment_page_link']
            if comment_page_link not in comment_page_link_list:
                comment_page_link_list.append(comment_page_link)
        return comment_page_link_list