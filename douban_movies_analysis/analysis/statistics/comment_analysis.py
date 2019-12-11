from __future__ import division, print_function
import pymongo
import jieba
from wordcloud import WordCloud
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
import seaborn as sns

from utils.utils import get_genre_dict, get_movie_genre_dict, get_comments_dataframe, init_stopwords, \
    get_genre_comments_words_dataframe, plot2y
from utils.utils import comment_df_year, comment_df_month

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['top_250_douban_movies']
dataframe = get_comments_dataframe()


# 对电影的每种类型生成对应的词云
def generate_genre_cloud():
    clouds_path = '../../cloud_imgs/genre_clouds/'
    comment_collection = db['comment_infos']
    movie_genres_dict = get_movie_genre_dict()
    genres_comments_dict = get_genre_dict()

    for comment_info in comment_collection.find():
        # 用电影名找到这个评论对应电影的类型
        comment_movie = comment_info['comment_movie_title']
        comment_movie = comment_movie.split(' ')[0]
        brief_comment = comment_info['brief_comment']
        comment_movie_genres_list = movie_genres_dict[comment_movie]

        for comment_movie_genre in comment_movie_genres_list:
            if comment_movie_genre in genres_comments_dict.keys():
                genres_comments_dict[comment_movie_genre].append(brief_comment)
            else:
                print('comment_movie_genre is not in the genres_comments_dict')
                print(comment_movie_genre)

    stop_words = init_stopwords()

    for genre in genres_comments_dict.keys():
        comment_words_df = get_genre_comments_words_dataframe(genre)
        comment_words_df = comment_words_df[~comment_words_df.comment_word.isin(stop_words.stopword)]

        # 统计词频
        words_stat = comment_words_df.groupby(by=['comment_word'])['comment_word'].agg({"计数": np.size})
        words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

        word_frequency = {x[0]: x[1] for x in words_stat.head(1000).values}

        store_path = clouds_path + str(genre)
        word_cloud = WordCloud(
            font_path="../../fonts/JingDianWeiBeiJian-1.ttf",
            background_color='white',
            max_words=200,
            max_font_size=200,
            width=1400,
            height=800
        )
        word_cloud.fit_words(word_frequency)
        word_cloud.to_file(store_path + ".jpg")


# 分析指定电影其短评的发表时间频率，即将时间跨度等分，统计每个时间跨度内的短评数量，可以绘图
def comments_year_frequency(rank_num=10):
    year_comment_df = dataframe.groupby('commenter').apply(comment_df_year)
    year_comment_statistics = year_comment_df.groupby('comment_timestamp')['util_num'].sum()
    year_comment_statistics = year_comment_statistics.sort_values(ascending=False).head(rank_num)
    return year_comment_statistics


def comments_month_frequency(rank_num=10):
    month_comment_df = dataframe.groupby('commenter').apply(comment_df_month)
    month_comment_statistics = month_comment_df.groupby('comment_timestamp')['util_num'].sum()
    month_comment_statistics = month_comment_statistics.sort_values(ascending=False).head(rank_num)
    return month_comment_statistics


def comments_day_frequency(rank_num=10):
    day_comment_df = dataframe.groupby('commenter')
    day_comment_statistics = day_comment_df.groupby('comment_timestamp')['util_num'].sum()
    day_comment_statistics = day_comment_statistics.sort_values(ascending=False).head(rank_num)
    return day_comment_statistics


def plot_time(movie_title):
    matplotlib.rc('figure', figsize=(14, 7))
    matplotlib.rc('font', size=14)
    matplotlib.rc('axes', grid=False)
    matplotlib.rc('axes', facecolor='white')

    data_com_X = dataframe[dataframe.comment_movie_title == movie_title]

    sns.distplot(data_com_X.comment_timestamp.apply(lambda x: int(x[0:4]) + float(int(x[5:7]) / 12.0))
                 , bins=100, kde=False, rug=True)
    plt.xlabel('time')
    plt.ylabel('Number of short_comment')
    img_path = './plot_time/' + movie_title + '.jpg'
    plt.savefig(img_path)
    plt.show()


def plot_stars(movie_title):
    data_com_X = dataframe[dataframe.comment_movie_title == movie_title]
    plot2y(x_data=data_com_X.comment_timestamp.apply(lambda x: int(x[0:4]) + float(float(x[5:7]) / 12.0))
           , x_label='time'
           , type1='scatter'
           , y1_data=data_com_X['comment_useful_upvote']
           , y1_color='#539caf'
           , y1_label='useful_num'
           , type2='scatter'
           , y2_data=data_com_X['comment_rating_stars']
           , y2_color='#7663b0'
           , y2_label='star'
           , title='Useful vote_up and star over Time')
    img_path = './plot_stars/' + movie_title + '.jpg'
    plt.savefig(img_path)
    plt.show()

if __name__ == '__main__':
    # generate_genre_cloud()
    plot_time("肖申克的救赎")
    # plot_stars("肖申克的救赎")
