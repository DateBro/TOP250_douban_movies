# -*- coding: utf-8 -*-
import random
import time
from logging import getLogger

import pymongo
import scrapy
from scrapy import Request
from pyquery import PyQuery as pq
import re
from TOP250_douban_movies.items import TOP250MovieInfoItem, MovieInfoItem, CommentInfoItem


class DoubanMoviesNoSeleniumSpider(scrapy.Spider):
    name = 'douban_movies_no_selenium'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250/', ]
    logger = getLogger(__name__)

    def start_requests(self):
        # 每次都要读取这次要开始爬的电影的链接index
        with open('/home/zhiyong/data/next_link_num.txt', 'rt') as f:
            next_link_index = f.read()
            next_link_index = int(next_link_index)

        # 将后面开始读的电影索引 + 8写入文件
        with open('/home/zhiyong/data/next_link_num.txt', 'wt') as f:
            new_next_link_index = next_link_index + 8
            f.write(str(new_next_link_index))

        # 从 douban_movies_2 数据库里面读取要看的电影的链接
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client['top_250_douban_movies_2']
        top_250_movie_infos_collection = db['top_250_movie_infos']
        movie_link_list = []
        for top_250_movie_info in top_250_movie_infos_collection.find():
            movie_link = top_250_movie_info['movie_link']
            movie_link_list.append(movie_link)

        for start in range(next_link_index, next_link_index + 4):
            if start >= 250:
                break
            movie_link = movie_link_list[start]
            time.sleep(1)
            self.logger.info(movie_link)
            yield Request(movie_link, callback=self.parse_movie_item)

            # 分别爬取好评，中评，差评
            choices = ['h', 'm', 'l']
            for choice in choices:
                # 爬取每种评论之前先sleep一段时间
                every_type_comments_sleep = random.randint(1, 2)
                time.sleep(every_type_comments_sleep)

                comment_suffix = 'comments?start=$&limit=20&sort=new_score&status=P'
                real_comments_link = movie_link + comment_suffix
                if choice == 'h':
                    real_comments_link = real_comments_link + '&percent_type=h'
                elif choice == 'l':
                    real_comments_link = real_comments_link + '&percent_type=l'
                else:
                    real_comments_link = real_comments_link + '&percent_type=m'
                for start in range(20):
                    every_type_comments_sleep = random.randint(1, 2)
                    time.sleep(every_type_comments_sleep)

                    real_comments_link = str.replace(real_comments_link, '$', str(start * 20))
                    # 然后可以爬取每个 movie 的短评信息
                    self.logger.info(real_comments_link)
                    yield Request(url=real_comments_link, callback=self.parse_comments)

    # def parse_top250(self, response):
    #     try:
    #         html = response.text
    #         doc = pq(html)
    #     except:
    #         self.logger.info('some error happened in pyquery response text')
    #     all_movies = doc('#content > div > div.article > ol > li > div > div.info')
    #     for movie in all_movies.items():
    #         # 爬每部电影的信息之前先sleep一段时间!
    #         # 但seleniumdownload页面的时候会sleep，先不sleep试试
    #         sleep_time = random.uniform(0.5, 1)
    #         time.sleep(sleep_time)
    #
    #         movie_link = movie('div.hd > a').attr('href')
    #         title = movie('div.hd > a > span.title').text()
    #         top250_movie_info_item = TOP250MovieInfoItem()
    #         top250_movie_info_item['title'] = title
    #         top250_movie_info_item['movie_link'] = movie_link
    #         self.logger.info(top250_movie_info_item)
    #         yield top250_movie_info_item
    #         # 然后发出爬取每个 movie 的具体信息的 request
    #         self.logger.info(movie_link)
    #         yield Request(movie_link, callback=self.parse_movie_item)
    #
    #         # 分别爬取好评，中评，差评
    #         choices = ['h', 'm', 'l']
    #         for choice in choices:
    #             # 爬取每种评论之前先sleep一段时间
    #             every_type_comments_sleep = random.randint(1, 2)
    #             time.sleep(every_type_comments_sleep)
    #
    #             comment_suffix = 'comments?start=$&limit=20&sort=new_score&status=P'
    #             real_comments_link = movie_link + comment_suffix
    #             if choice == 'h':
    #                 real_comments_link = real_comments_link + '&percent_type=h'
    #             elif choice == 'l':
    #                 real_comments_link = real_comments_link + '&percent_type=l'
    #             else:
    #                 real_comments_link = real_comments_link + '&percent_type=m'
    #             try:
    #                 for start in range(20):
    #                     every_type_comments_sleep = random.randint(1, 2)
    #                     time.sleep(every_type_comments_sleep)
    #
    #                     real_comments_link = str.replace(real_comments_link, '$', str(start * 20))
    #                     # 然后可以爬取每个 movie 的短评信息
    #                     self.logger.info(real_comments_link)
    #                     yield Request(url=real_comments_link, callback=self.parse_comments)
    #             except Exception:
    #                 self.logger.info('exception happen in get movie comment infos')
    #                 time.sleep(5)
    #                 continue

    def parse_movie_item(self, response):
        time.sleep(1)
        movie_info_item = MovieInfoItem()
        try:
            html = response.text
            anti_spider_warn = '检测到有异常请求'
            if anti_spider_warn in html:
                print(anti_spider_warn, 'can not get response!')
            else:
                doc = pq(html)
                title = doc('#content > h1 > span:nth-child(1)').text()
                year = doc('#content > h1 > span.year').text()
                director = doc('#info > span:nth-child(1) > span.attrs > a').text()
                main_roles = doc('#info > span.actor > span.attrs').text()
                movie_genre = response.xpath('.//span[@property="v:genre"]/text()').extract()
                # 以后可能会爬取语言和国家之类的
                rating_num = doc('#interest_sectl > div:nth-child(1) > div.rating_self.clearfix > strong').text()
                rating_people_num = doc(
                    '#interest_sectl > div:nth-child(1) > div.rating_self.clearfix > div > div.rating_sum > a > span').text()
                star_5_percentage = doc(
                    '#interest_sectl > div:nth-child(1) > div.ratings-on-weight > div:nth-child(1) > span.rating_per').text()
                star_4_percentage = doc(
                    '#interest_sectl > div:nth-child(1) > div.ratings-on-weight > div:nth-child(2) > span.rating_per').text()
                star_3_percentage = doc(
                    '#interest_sectl > div:nth-child(1) > div.ratings-on-weight > div:nth-child(3) > span.rating_per').text()
                star_2_percentage = doc(
                    '#interest_sectl > div:nth-child(1) > div.ratings-on-weight > div:nth-child(4) > span.rating_per').text()
                star_1_percentage = doc(
                    '#interest_sectl > div:nth-child(1) > div.ratings-on-weight > div:nth-child(5) > span.rating_per').text()
                rating_related_info = {'rating_num': rating_num,
                                       'rating_people_num': rating_people_num,
                                       'star_5_percentage': star_5_percentage,
                                       'star_4_percentage': star_4_percentage,
                                       'star_3_percentage': star_3_percentage,
                                       'star_2_percentage': star_2_percentage,
                                       'star_1_percentage': star_1_percentage}
                brief_intro = doc('#link-report > span.short > span').text()

                comment_num = doc('#comments-section > div.mod-hd > h2 > span > a').text()
                comment_num = re.search(r"\d+", comment_num).group(0)
                comment_num = int(comment_num)
                comments_link = doc('#comments-section > div.mod-hd > h2 > span > a').attr('href')

                movie_info_item['title'] = title
                movie_info_item['year'] = year
                movie_info_item['director'] = director
                movie_info_item['main_roles'] = main_roles
                movie_info_item['rating_related_info'] = rating_related_info
                movie_info_item['brief_intro'] = brief_intro
                movie_info_item['comment_num'] = comment_num
                movie_info_item['comments_link'] = comments_link
                movie_info_item['movie_genre'] = movie_genre

                self.logger.info(movie_info_item)

                yield movie_info_item
        except Exception:
            self.logger.info('some bugs happen in parse_movie_item')
            yield movie_info_item

    def parse_comments(self, response):
        comment_info_item = CommentInfoItem()
        try:
            if response.status == 500:
                self.logger.info('response 500 in parse_comments')
                yield comment_info_item
            else:
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
                        print(comment_rating_class_value)

                    comment_info_item['commenter'] = commenter
                    comment_info_item['commenter_link'] = commenter_link
                    comment_info_item['brief_comment'] = brief_comment
                    comment_info_item['comment_useful_upvote'] = comment_useful_upvote
                    comment_info_item['comment_timestamp'] = comment_timestamp
                    comment_info_item['comment_rating_stars'] = comment_rating_stars
                    comment_info_item['comment_movie_title'] = comment_movie_title

                    self.logger.info(comment_info_item)

                    yield comment_info_item
        except:
            self.logger.info('some bugs happen in parse_comments')
            yield comment_info_item
