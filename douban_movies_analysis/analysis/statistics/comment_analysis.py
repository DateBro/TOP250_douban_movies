import pymongo
import jieba
from utils.utils import get_genre_dict, generate_cloud, get_movie_genre_dict, get_comments_dataframe
from utils.utils import comment_df_year, comment_df_month

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['top_250_douban_movies']
dataframe = get_comments_dataframe()

# 后面添加针对某一部特定电影的影评分析

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

    for genres in genres_comments_dict.keys():
        comment_list = genres_comments_dict[genres]
        comment_agg = ''
        for comment in comment_list:
            single_comment_seq = " ".join(jieba.cut(comment))
            comment_agg += single_comment_seq
        genres_comments_dict[genres] = comment_agg

        store_path = clouds_path + str(genres)
        word_cloud = generate_cloud(comment_agg)
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

if __name__ == '__main__':
    generate_genre_cloud()
