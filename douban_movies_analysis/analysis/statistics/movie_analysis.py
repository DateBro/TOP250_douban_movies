import pymongo
import jieba
from utils.utils import get_movie_comments_dict, generate_cloud, get_genre_dict

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['top_250_douban_movies']

# 对每部电影电影生成对应的词云
def generate_movie_cloud():
    clouds_path = './cloud_imgs/movie_clouds/'
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

    for movie_title in movie_comments_dict.keys():
        comment_list = movie_comments_dict[movie_title]
        comment_agg = ''
        for comment in comment_list:
            single_comment_seq = " ".join(jieba.cut(comment))
            comment_agg += single_comment_seq
        movie_comments_dict[movie_title] = comment_agg

        store_path = clouds_path + str(movie_title)
        word_cloud = generate_cloud(comment_agg)
        word_cloud.to_file(store_path + ".jpg")

# 总评分最高的前10部电影
def stars_movies(rank_num=10):
    movie_stars_dict = {}
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_title = movie_info['movie_title']
        movie_stars = movie_info['rating_related_info']['rating_num']
        movie_stars_dict[movie_title] = movie_stars

    ranked_list = sorted(movie_stars_dict.items(), key=lambda item:item[1],reverse=True)
    ranked_list = ranked_list[:rank_num]
    ranked_dict = {}
    for l in ranked_list:
        ranked_dict[l[0]] = l[1]
    return ranked_dict

# 分析电影上映年份的电影数量，可以绘图
# 可以回头看一下DataFrame和matplotlib的操作
def year_movies():
    pass

# 有时间的话可以分析电影一到五星百分比，并绘图
def stars_percentage_movies():
    pass

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
    director_movies_dict = {}
    movie_infos_collection = db['movie_infos']
    for movie_info in movie_infos_collection.find():
        movie_director = movie_info['director']
        if movie_director not in director_movies_dict.keys():
            director_movies_dict[movie_director] = 1
        else:
            director_movies_dict[movie_director] += 1

    ranked_list = sorted(director_movies_dict.items(), key=lambda item:item[1],reverse=True)
    ranked_list = ranked_list[:rank_num]
    ranked_dict = {}
    for l in ranked_list:
        ranked_dict[l[0]] = l[1]
    return ranked_dict

# 分析前十名上榜电影最多的演员
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
    ranked_list = sorted(roles_movies_dict.items(),key=lambda item:item[1],reverse=True)
    ranked_list = ranked_list[:rank_num]
    ranked_dict = {}
    for l in ranked_list:
        ranked_dict[l[0]] = l[1]
    return ranked_dict

if __name__ == '__main__':
    pass