# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class MovieInfoItem(Item):
    collection = 'movie_infos'

    title = Field()
    year = Field()
    director = Field()
    main_roles = Field()
    styles = Field()
    rating_related_info = Field()
    brief_intro = Field()
    comment_num = Field()
    comments_link = Field()
    movie_genre = Field()

class TOP250MovieInfoItem(Item):
    collection = 'top_250_movie_infos'

    title = Field()
    movie_link = Field()

class CommentInfoItem(Item):
    collection = 'comment_infos'

    commenter = Field()
    commenter_link = Field()
    brief_comment = Field()
    comment_timestamp = Field()
    comment_rating_stars = Field()
    comment_useful_upvote = Field()
    comment_movie_title = Field()
    comment_page_link = Field()

class CommenterInfoItem(Item):
    collection = 'commenter_infos'

    commenter_link = Field()
    location = Field()
    register_timestamp = Field()
    account_name = Field()
    following_num = Field()
    follower_num = Field()
    # 暂时先准备这么多用户信息