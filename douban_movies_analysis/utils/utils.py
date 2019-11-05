import jieba
import pymongo
import pandas as pd

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['top_250_douban_movies_test']

def get_movie_dataframe():
    movie_info_dict_list = []
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_info_dict = {}
        movie_genre_list = movie_info['movie_genre']
        movie_title = movie_info['title']
        movie_title = movie_title.split(' ')[0]
        rating_related_info = movie_info['rating_related_info']

        movie_info_dict['movie_title'] = movie_title
        movie_info_dict['year'] = movie_info['year']
        movie_info_dict['director'] = movie_info['director']
        movie_info_dict['main_roles'] = movie_info['main_roles']
        movie_info_dict['comment_num'] = movie_info['comment_num']
        movie_info_dict['rating_num'] = rating_related_info['rating_num']
        movie_info_dict['rating_people_num'] = rating_related_info['rating_people_num']
        movie_info_dict['star_5_percentage'] = rating_related_info['star_5_percentage']
        movie_info_dict['star_4_percentage'] = rating_related_info['star_4_percentage']
        movie_info_dict['star_3_percentage'] = rating_related_info['star_3_percentage']
        movie_info_dict['star_2_percentage'] = rating_related_info['star_2_percentage']
        movie_info_dict['star_1_percentage'] = rating_related_info['star_1_percentage']
        movie_info_dict['comments_link'] = movie_info['comments_link']
        # genre 的处理暂时先这样
        movie_info_dict['movie_genre_list'] = movie_genre_list
        movie_info_dict['brief_intro'] = movie_info['brief_intro']
        movie_info_dict['util_num'] = 1

        movie_info_dict_list.append(movie_info_dict)

    movie_info_dataframe = pd.DataFrame(movie_info_dict_list)

    return movie_info_dataframe

def get_movie_info_dict_list():
    movie_info_dict_list = []
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_info_dict = {}
        movie_genre_list = movie_info['movie_genre']
        movie_title = movie_info['title']
        movie_title = movie_title.split(' ')[0]
        rating_related_info = movie_info['rating_related_info']

        movie_info_dict['movie_title'] = movie_title
        movie_info_dict['year'] = movie_info['year']
        movie_info_dict['director'] = movie_info['director']
        movie_info_dict['main_roles'] = movie_info['main_roles']
        movie_info_dict['comment_num'] = movie_info['comment_num']
        movie_info_dict['rating_num'] = rating_related_info['rating_num']
        movie_info_dict['rating_people_num'] = rating_related_info['rating_people_num']
        movie_info_dict['star_5_percentage'] = rating_related_info['star_5_percentage']
        movie_info_dict['star_4_percentage'] = rating_related_info['star_4_percentage']
        movie_info_dict['star_3_percentage'] = rating_related_info['star_3_percentage']
        movie_info_dict['star_2_percentage'] = rating_related_info['star_2_percentage']
        movie_info_dict['star_1_percentage'] = rating_related_info['star_1_percentage']
        movie_info_dict['comments_link'] = movie_info['comments_link']
        # genre 的处理存疑
        movie_info_dict['movie_genre_list'] = movie_genre_list
        movie_info_dict['brief_intro'] = movie_info['brief_intro']

        movie_info_dict_list.append(movie_info_dict)

    return movie_info_dict_list

# 获取每个以genre为key，评论（初始为空列表）的dictionary
def get_genre_dict():
    genres_dict = dict()
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_genre_list = movie_info['movie_genre']
        for movie_genre in movie_genre_list:
            if movie_genre not in genres_dict.keys():
                genres_dict[movie_genre] = list()
    return genres_dict

# 获得以movie_title为key，comments list为value的dictionary
def get_movie_comments_dict():
    movie_comments_dict = dict()
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_title = movie_info['title']
        movie_title = movie_title.split(' ')[0]
        movie_comments_dict[movie_title] = list()
    return movie_comments_dict

# 返回以movie_title为key，genre列表为value的dictionary
def get_movie_genre_dict():
    movie_genre_dict = dict()
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_genre_list = movie_info['movie_genre']
        movie_title = movie_info['title']
        movie_title = movie_title.split(' ')[0]
        movie_genre_dict[movie_title] = movie_genre_list
    return movie_genre_dict

def get_comments_dataframe():
    comments_info_dict_list = []
    comment_infos_collection = db['comment_infos']
    for comment_info in comment_infos_collection.find():
        comment_info_dict = {}

        comment_info_dict['commenter'] = comment_info['commenter']
        comment_info_dict['commenter_link'] = comment_info['commenter_link']
        comment_info_dict['brief_comment'] = comment_info['brief_comment']
        comment_info_dict['comment_useful_upvote'] = comment_info['comment_useful_upvote']
        comment_info_dict['comment_timestamp'] = comment_info['comment_timestamp']
        comment_info_dict['comment_rating_stars'] = comment_info['comment_rating_stars']
        comment_info_dict['comment_movie_title'] = comment_info['comment_movie_title']
        # comment_info_dict['comment_page_link'] = comment_info['comment_page_link']
        comment_info_dict['util_num'] = 1

        comments_info_dict_list.append(comment_info_dict)

    comment_info_dataframe = pd.DataFrame(comments_info_dict_list)

    return comment_info_dataframe

def comment_df_year(comment_df):
    comment_df['comment_timestamp'] = comment_df['comment_timestamp'].str.slice(0, 4)
    return comment_df

def comment_df_month(comment_df):
    comment_df['comment_timestamp'] = comment_df['comment_timestamp'].str.slice(0, 7)
    return comment_df

def get_movie_comments_words_dataframe(movie_title='肖申克的救赎'):
    brief_comments_list = []
    comment_infos_collection = db['comment_infos']
    for comment_info in comment_infos_collection.find():
        comment_movie_title = comment_info['comment_movie_title']
        if comment_movie_title == movie_title:
            brief_comments_list.append(comment_info['brief_comment'])

    comment_words = []
    for comment in brief_comments_list:
        comment_seqs = jieba.lcut(comment)
        for single_comment_seq in comment_seqs:
            comment_words.append(single_comment_seq)

    comment_words_df = pd.DataFrame({'comment_word': comment_words})
    return comment_words_df

def get_movie_dataframe():
    movie_info_dict_list = []
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_info_dict = {}
        movie_genre_list = movie_info['movie_genre']
        movie_title = movie_info['title']
        movie_title = movie_title.split(' ')[0]
        rating_related_info = movie_info['rating_related_info']

        movie_info_dict['movie_title'] = movie_title
        movie_info_dict['year'] = movie_info['year']
        movie_info_dict['director'] = movie_info['director']
        movie_info_dict['main_roles'] = movie_info['main_roles']
        movie_info_dict['comment_num'] = movie_info['comment_num']
        movie_info_dict['rating_num'] = rating_related_info['rating_num']
        movie_info_dict['rating_people_num'] = rating_related_info['rating_people_num']
        movie_info_dict['star_5_percentage'] = rating_related_info['star_5_percentage']
        movie_info_dict['star_4_percentage'] = rating_related_info['star_4_percentage']
        movie_info_dict['star_3_percentage'] = rating_related_info['star_3_percentage']
        movie_info_dict['star_2_percentage'] = rating_related_info['star_2_percentage']
        movie_info_dict['star_1_percentage'] = rating_related_info['star_1_percentage']
        movie_info_dict['comments_link'] = movie_info['comments_link']
        # genre 的处理暂时先这样
        movie_info_dict['movie_genre_list'] = movie_genre_list
        movie_info_dict['brief_intro'] = movie_info['brief_intro']
        movie_info_dict['util_num'] = 1

        movie_info_dict_list.append(movie_info_dict)

    movie_info_dataframe = pd.DataFrame(movie_info_dict_list)

    return movie_info_dataframe

def init_stopwords():
    stopwords = pd.read_csv("../../data/哈工大停用词表.txt", index_col=False, quoting=3, sep="\t", names=['stopword'], encoding='utf-8')
    return stopwords

def get_genre_comments_words_dataframe(genre='剧情'):
    brief_comments_list = []
    comment_infos_collection = db['comment_infos']
    comment_movie_genre_dict = get_movie_genre_dict()
    for comment_info in comment_infos_collection.find():
        comment_movie_title = comment_info['comment_movie_title']
        comment_movie_genre_list = comment_movie_genre_dict[comment_movie_title]
        if genre in comment_movie_genre_list:
            brief_comments_list.append(comment_info['brief_comment'])

    comment_words = []
    for comment in brief_comments_list:
        comment_seqs = jieba.lcut(comment)
        for single_comment_seq in comment_seqs:
            comment_words.append(single_comment_seq)

    comment_words_df = pd.DataFrame({'comment_word': comment_words})
    return comment_words_df