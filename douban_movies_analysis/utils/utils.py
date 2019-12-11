import re
import jieba
import pymongo
import pandas as pd
from matplotlib import pyplot as plt
import geopandas as gp
import numpy as np
import matplotlib
import seaborn as sns

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['top_250_douban_movies_test']
stop_words_file = "../../data/百度停用词表.txt"


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
        movie_info_dict['year'] = int(movie_info['year'][1:5])
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
    stopwords = pd.read_csv(stop_words_file, index_col=False, quoting=3, sep="\t", names=['stopword'], encoding='utf-8')
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


def get_commenters_dataframe():
    commenters_info_dict_list = []
    commenter_infos_collection = db['commenter_infos']
    for commenter_info in commenter_infos_collection.find():
        commenter_info_dict = {}

        commenter_info_dict['commenter_link'] = commenter_info['commenter_link']
        commenter_info_dict['location'] = commenter_info['location']
        commenter_info_dict['register_timestamp'] = commenter_info['register_timestamp']
        commenter_info_dict['account_name'] = commenter_info['account_name']
        try:
            commenter_info_dict['following_num'] = int(commenter_info['following_num'])
        except Exception:
            commenter_info_dict['following_num'] = 0

        try:
            commenter_info_dict['follower_num'] = int(commenter_info['follower_num'])
        except Exception:
            commenter_info_dict['follower_num'] = 0
        commenter_info_dict['util_num'] = 1

        commenters_info_dict_list.append(commenter_info_dict)

    commenter_info_dataframe = pd.DataFrame(commenters_info_dict_list)

    # 去掉空值
    commenter_info_dataframe = commenter_info_dataframe[~commenter_info_dataframe.location.apply(lambda x: not (x[:]))]

    return commenter_info_dataframe


def plot2y(x_data, x_label, type1, y1_data, y1_color, y1_label, type2, y2_data, y2_color, y2_label, title):
    _, ax1 = plt.subplots()

    if type1 == 'hist':
        ax1.hist(x_data, histtype='stepfilled', bins=200, color=y1_color)
        ax1.set_ylabel(y1_label, color=y1_color)
        ax1.set_xlabel(x_label)
        ax1.set_yscale('symlog')
        ax1.set_title(title)

    elif type1 == 'plot':
        ax1.plot(x_data, y1_data, color=y1_color)
        ax1.set_ylabel(y1_label, color=y1_color)
        ax1.set_xlabel(x_label)
        ax1.set_yscale('linear')
        ax1.set_title(title)

    elif type1 == 'scatter':
        ax1.scatter(x_data, y1_data, color=y1_color, s=10, alpha=0.75)
        ax1.set_ylabel(y1_label, color=y1_color)
        ax1.set_xlabel(x_label)
        ax1.set_yscale('symlog')
        ax1.set_title(title)

    if type2 == 'bar':
        ax2 = ax1.twinx()
        ax2.bar(x_data, y2_data, color=y2_color, alpha=0.75)
        ax2.set_ylabel(y2_label, color=y2_color)
        ax2.set_yscale('linear')
        ax2.spines['right'].set_visible(True)

    elif type2 == 'scatter':
        ax2 = ax1.twinx()
        ax2.scatter(x_data, y2_data, color=y2_color, s=10, alpha=0.75)
        ax2.set_ylabel(y2_label, color=y2_color)
        ax2.set_yscale('linear')
        ax2.spines['right'].set_visible(True)


def locaP(x):
    prov_dic = {'黑龙江': '黑龙江省', '内蒙': '内蒙古自治区', '新疆': '新疆维吾尔自治区'
        , '吉林': '吉林省', '辽宁': '辽宁省', '甘肃': '甘肃省', '河北': '河北省'
        , '北京': '北京市', '山西': '山西省', '天津': '天津市', '陕西': '陕西省'
        , '宁夏': '宁夏回族自治区', '青海': '青海省', '山东': '山东省'
        , '西藏': '西藏自治区'
        , '河南': '河南省', '江苏': '江苏省', '安徽': '安徽省', '四川': '四川省'
        , '湖北': '湖北省', '重庆': '重庆市', '上海': '上海市', '浙江': '浙江省'
        , '湖南': '湖南省', '江西': '江西省', '云南': '云南省', '贵州': '贵州省'
        , '福建': '福建省', '广西': '广西壮族自治区', '台湾': '台湾省', '广东': '广东省'
        , '香港': '香港特别行政区', '澳门': '香港特别行政区', '海南': '海南省'
        , '苏州': '江苏省', '威海': '山东省', '嘉兴': '浙江省', '锡林浩特': '内蒙古自治区'
        , '温州': '浙江省', '肇庆': '广东省', '红河': '云南省', '延边': '吉林省'
        , '衢州': '浙江省', '伊宁': '新疆维吾尔自治区', '遵义': '贵州省', '绍兴': '浙江省'
        , '库尔勒': '新疆维吾尔自治区', '杭州': '浙江省', '通化': '吉林省'}

    for d in prov_dic:
        if d in x:  return prov_dic[d]


def locaC(x):
    country_dict = {'China': 'China', 'United States': 'United States'
        , 'Hong Kong': 'Hong Kong', 'Taiwan': 'Taiwan, Province of China'
        , 'Japan': 'Japan', 'Korea': 'Korea, Republic of'
        , 'United Kingdom': 'United Kingdom', 'France': 'France'
        , 'Germany': 'Germany'
        , 'Italy': 'Italy', 'Spain': 'Spain', 'India': 'India'
        , 'Thailand': 'Thailand', 'Russia': 'Russian Federation'
        , 'Iran': 'Iran', 'Canada': 'Canada', 'Australia': 'Australia'
        , 'Ireland': 'Ireland', 'Sweden': 'Sweden'
        , 'Brazil': 'Brazil', 'Denmark': 'Denmark'
        , 'Singapore': 'Singapore', 'Cuba': 'Cuba', 'Iceland': 'Iceland'
        , 'Netherlands': 'Netherlands', 'Switzerland': 'Switzerland'
        , 'Bahamas': 'Bahamas', 'Sierra Leone': 'Sierra Leone'
        , 'Finland': 'Finland', 'Czech Republic': 'Czech Republic'
        , 'Egypt': 'Egypt', 'Turkey': 'Turkey', 'Argentina': 'Argentina'
        , 'Bolivia': 'Bolivia'
        , 'Norway': 'Norway', 'Indonesia': 'Indonesia'
        , 'Chile': 'Chile', 'Morocco': 'Morocco', 'Andorra': 'Andorra'
        , 'Senegal': 'Senegal'
        , 'Somalia': 'Somalia', 'Haiti': 'Haiti', 'Portugal': 'Portugal'
        , 'Togo': 'Togo', 'New Zealand': 'New Zealand'
        , 'Hungary': 'Hungary', 'Bulgaria': 'Bulgaria'
        , 'Afghanistan': 'Afghanistan', 'Niue': 'Niue', 'Austria': 'Austria'
        , 'Peru': 'Peru', 'Greece': 'Greece', 'Luxembourg': 'Luxembourg'
        , 'Greenland': 'Greenland', 'Fiji': 'Fiji', 'Jordan': 'Jordan'
        , 'Reunion': 'Reunion', 'Bhutan': 'Bhutan', 'Barbados': 'Barbados'
        , 'Malaysia': 'Malaysia', 'Ghana': 'Ghana'
        , 'Poland': 'Poland', 'Guinea': 'Guinea', 'Belgium': 'Belgium'
        , 'Zimbabwe': 'Zimbabwe', 'Aruba': 'Aruba', 'Anguilla': 'Anguilla'
        , 'Nepal': 'Nepal', 'Latvia': 'Latvia'
        , 'Philippines': 'Philippines'
        , 'United Arab Emirates': 'United Arab Emirates'
        , 'Saudi Arabia': 'Saudi Arabia'
        , 'South Africa': 'South Africa', 'Mexico': 'Mexico'
        , 'Syrian': 'Syrian Arab Republic'
        , 'Sudan': 'Sudan', 'Iraq': 'Iraq', 'Slovenia': 'Slovenia'
        , 'Tunisia': 'Tunisia', 'Nicaragua': 'Nicaragua'
        , 'Kazakhstan': 'Kazakhstan'
        , 'Bahrain': 'Bahrain', 'Vietnam': 'Viet Nam'
        , 'Tuvalu': 'Tuvula', 'Vatican City': 'Vatican City State (Holy See)'
        , 'Wallis et Futuna': 'Wallis and Futuna Islands'
        , 'Tanzania': 'Tanzania, United Republic of'
        , 'Libya': 'Liby An Arab Jamahiriya'
        , 'Western Sahara': 'Western Sahara'
        , 'Syria': 'Syrian Arab Republic'
        , 'Faroe Islands': 'Faroe Islands'
        , 'Sao Tome and Principe': 'Sao Tome and Principe'
        , 'Christmas Islands': 'Christmas Islands'
        , 'Costa Rica': 'Costa Rica', 'Antarctica': 'Antartica'
        , 'Cook Islands': 'Cook Islands', 'Kuwait': 'Kuwait', 'Bermuda': 'Bermuda'
        , 'El Salvador': 'El Salvador'
        , 'Ethiopia': 'Ethiopia', 'Mozambique': 'Mozambique'
        , 'Guyana': 'Guyana', 'Mongolia': 'Mongolia'
        , 'Eritrea': 'Eritrea'
        , 'Monaco': 'Monaco', 'Gibraltar': 'Gibralter'
        , 'Yemen': 'Yemen', 'Micronesia': 'Micronesia, (Federated States of)'
        , 'Colombia': 'Columbia', 'Guadeloupe': 'Guadeloupe'
        , 'Antigua': 'Antigua & Barbuda', 'Caledonia': 'New Caledonia'
        , 'Cambodia': 'Cambodia'
        , 'Franch Guiana': 'French Guiana', 'Vanuatu': 'Vanuatu'
        , 'Puerto Rico': 'Puerto Rico'
        , 'Belize': 'Belize', 'Angola': 'Angola', 'Dominica': 'Dominica'
        , 'Albania': 'Albania', 'Azerbaijan': 'Azerbaijan'
        , 'Ukraine': 'Ukraine', 'Grenada': 'Grenada'
        , 'Panama': 'Panama', 'Israel': 'Israel', 'Guatemala': 'Guatemala'
        , 'Belarus': 'Belarus', 'Cameroon': 'Cameroon'
        , 'Jamaica': 'Jamaica', 'Warwickshire': 'United Kingdom'
        , 'Madagascar': 'Madagascar', 'Mali': 'Mali'
        , 'Tokelau': 'Tokelau', 'Benin': 'Benin', 'Malta': 'Malta'
        , 'Gabon': 'Gabon', 'Algeria': 'Algeria'
        , 'Kildare': 'Ireland', 'Ecuador': 'Ecuador', 'Pakistan': 'Pakistan'
        , 'Chad': 'Chad', 'Paraguay': 'Paraguay', 'Leicestershire': 'Ireland'
        , 'Estonia': 'Estonia', 'Maldives': 'Maldives'
        , 'Liechtenstein': 'Liechtenstein', 'Cyprus': 'Cyprus'
        , 'Zambia': 'Zambia'
        , 'Macedonia': 'Macedonia, The Former Republic of Yugoslavia'
        , 'Bouvet': 'Bouvet Island', 'Uganda': 'Uganda'
        , 'Northern Marianas': 'Northern Mariana Islands'
        , 'Miquelon': 'St. Pierre and Miquelon', 'Pitcairn': 'Pitcairn'
        , 'Slovakia': 'Slovakia', 'Norfolk': 'Norfolk Island'
        , 'Lanka': 'Sri Lanka', 'Congo': 'Congo'
        , 'Cocos': 'Cocos (Keeling) Islands', 'Serbia': 'Bulgaria'
        , 'Croatia': 'Croatia'
        , 'Palestinian': 'Israel', 'Armenia': 'Armenia'
        , 'Saint Barthélemy': 'France', 'Sint Maarten': 'France'
        , 'Côte': "Cote D'ivoire (Ivory Coast)"
        , 'Jersey': 'United Kingdom', 'Isle of Man': 'United Kingdom'
        , 'Aland Islands': 'Finland', 'Kosovo': 'Yugoslavia'
        , 'Montenegro': 'Yugoslavia'}
    for d in country_dict:
        if d in x:  return country_dict[d]


def geod_world(df, title, legend=False):
    matplotlib.rc('figure', figsize=(14, 7))
    matplotlib.rc('font', size=14)
    matplotlib.rc('axes', grid=False)
    matplotlib.rc('axes', facecolor='white')

    world_geod = gp.GeoDataFrame.from_file(
        'E:/PycharmProjects/douban_movies_analysis/data/world_countries_shp/World_countries_shp.shp')
    data_geod = gp.GeoDataFrame(df)
    da_merge = world_geod.merge(data_geod, on='NAME', how='left')
    sum(np.isnan(da_merge['NUM']))
    da_merge['NUM'][np.isnan(da_merge['NUM'])] = 14.0
    da_merge.plot('NUM', k=20, cmap=plt.cm.Blues, alpha=1, legend=legend)
    plt.title(title, fontsize=15)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())


def geod_china(df, title, legend=False):
    matplotlib.rc('figure', figsize=(14, 7))
    matplotlib.rc('font', size=14)
    matplotlib.rc('axes', grid=False)
    matplotlib.rc('axes', facecolor='white')

    china_geod = gp.GeoDataFrame.from_file(
        'E:/PycharmProjects/douban_movies_analysis/data/china_shp/中国地图shp格式/shp格式2/map/bou2_4p.shp', encoding='gb18030')
    data_geod = gp.GeoDataFrame(df)
    da_merge = china_geod.merge(data_geod, on='NAME', how='left')
    sum(np.isnan(da_merge['NUM']))
    da_merge['NUM'][np.isnan(da_merge['NUM'])] = 14.0
    da_merge.plot('NUM', k=20, cmap=plt.cm.Blues, alpha=1, legend=legend)
    plt.title(title, fontsize=15)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
