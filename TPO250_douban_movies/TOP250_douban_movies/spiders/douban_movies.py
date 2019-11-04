# -*- coding: utf-8 -*-
import random
import time
import scrapy
from scrapy import Request
from pyquery import PyQuery as pq
import re
from TOP250_douban_movies.items import TOP250MovieInfoItem, MovieInfoItem


class TOP250MovieInfosSpider(scrapy.Spider):
    name = 'douban_movies'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250/',]

    def start_requests(self):
        base_url = 'https://movie.douban.com/top250?start=$&filter='
        for start in range(10):
            url = str.replace(base_url, '$', str(start * 25))
            self.logger.info(url)
            yield Request(url, callback=self.parse_top250)

    def parse_top250(self, response):
        top250_movie_info_item = TOP250MovieInfoItem()
        html = response.text
        doc = pq(html)
        all_movies = doc('#content > div > div.article > ol > li > div > div.info')
        for movie in all_movies.items():
            # 爬每部电影的信息之前先sleep一段时间!
            # 但seleniumdownload页面的时候会sleep，先不sleep试试
            sleep_time = random.uniform(0.5, 1)
            time.sleep(sleep_time)

            movie_link = movie('div.hd > a').attr('href')
            title = movie('div.hd > a > span.title').text()
            top250_movie_info_item['title'] = title
            top250_movie_info_item['movie_link'] = movie_link
            self.logger.info(top250_movie_info_item)
            yield top250_movie_info_item
            # 然后发出爬取每个 movie 的具体信息的 request
            self.logger.info(movie_link)
            yield Request(movie_link, callback=self.parse_movie_item)

    def parse_movie_item(self, response):
        movie_info_item = MovieInfoItem()
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