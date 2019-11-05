import pymongo
import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud

from utils.utils import get_movie_comments_dict, get_genre_dict, get_movie_info_dict_list, \
    get_movie_dataframe, get_movie_comments_words_dataframe, init_stopwords

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['top_250_douban_movies_test']
dataframe = get_movie_dataframe()

# 对每部电影电影生成对应的词云
def generate_movie_cloud():
    clouds_path = '../../cloud_imgs/movie_clouds/'
    comment_collection = db['comment_infos']
    # 先得到250部电影的title
    movie_comments_dict = get_movie_comments_dict()
    comment_infos = comment_collection.find()
    for comment_info in comment_infos:
        comment_movie = comment_info['comment_movie_title']
        comment_movie = comment_movie.split(' ')[0]
        brief_comment = comment_info['brief_comment']
        if comment_movie in movie_comments_dict.keys():
            movie_comments_dict[comment_movie].append(brief_comment)
        else:
            print('this movie is not in the dict')
            print(comment_movie)

    stop_words = init_stopwords()

    for movie_title in movie_comments_dict.keys():
        comment_words_df = get_movie_comments_words_dataframe(movie_title)
        comment_words_df = comment_words_df[~comment_words_df.comment_word.isin(stop_words.stopword)]

        # 统计词频
        words_stat = comment_words_df.groupby(by=['comment_word'])['comment_word'].agg({"计数": np.size})
        words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

        word_frequency = {x[0]: x[1] for x in words_stat.head(1000).values}

        store_path = clouds_path + str(movie_title)
        word_cloud = WordCloud(
            font_path="../../fonts/JingDianWeiBeiJian-1.ttf",
            background_color='white',
            max_words=2000,
            max_font_size=40,
            width=1000,
            height=500
        )
        word_cloud.fit_words(word_frequency)
        word_cloud.to_file(store_path + ".jpg")

# 总评分最高的前10部电影
def stars_movies(rank_num=10):
    return dataframe.sort_values('rating_num', ascending=False)[['movie_title','rating_num']].head(rank_num)

# 分析电影上映年份的电影数量，可以绘图
def year_movies(rank_num=10):
    # 改用 DataFrame 简洁的 API 实现
    year_statistics = dataframe.groupby('year')['util_num'].sum()
    year_statistics = year_statistics.sort_values(ascending=False).head(rank_num)
    return year_statistics
    # 后面可以写一下将统计数据绘图的方法

# 分析每个电影类型所有的电影数量
def genre_movies():
    genre_dict = get_genre_dict()
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_genre_list = movie_info['movie_genre']
        for movie_genre in movie_genre_list:
            if genre_dict[movie_genre] == []:
                genre_dict[movie_genre] = 1
            else:
                genre_dict[movie_genre] = genre_dict[movie_genre]+1
    return genre_dict

# 分析前十名上榜电影最多的导演
def director_movies(rank_num = 10):
    director_statistics = dataframe.groupby('director')['util_num'].sum()
    director_statistics = director_statistics.sort_values(ascending=False).head(rank_num)
    return director_statistics

# 分析前十名上榜电影最多的演员
# 暂时不知道如何使用 DataFrame 的 API 修改
def roles_movies(rank_num = 10):
    roles_movies_dict = {}
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        main_roles_list = movie_info['main_roles'].split('/')
        for role in main_roles_list:
            role = str.replace(role, ' ', '')
            if role not in roles_movies_dict.keys():
                roles_movies_dict[role] = 1
            else:
                roles_movies_dict[role] += 1
    ranked_list = sorted(roles_movies_dict.items(), key=lambda item: item[1], reverse=True)
    ranked_list = ranked_list[:rank_num]
    ranked_dict = {}
    for l in ranked_list:
        ranked_dict[l[0]] = l[1]
    return ranked_dict

# 分析评论数前rank_num名电影
def comments_num_movies(rank_num=10):
    comments_num_statistics = dataframe.sort_values('comment_num', ascending=False)[['movie_title', 'comment_num']].head(rank_num)
    return comments_num_statistics

# 分析投票数前rank_num名电影
def rating_people_num_movies(rank_num=10):
    rating_people_num_statistics = dataframe.sort_values('rating_people_num', ascending=False)[['movie_title', 'rating_people_num']].head(rank_num)
    return rating_people_num_statistics

if __name__ == '__main__':
    # year_movies()
    generate_movie_cloud()