import numpy as np
import matplotlib.pyplot as plt

from utils.utils import get_movie_info_dict_list, get_movie_dataframe, get_comments_dataframe, comment_df_year, comment_df_month


plt.style.use('seaborn-white')
data = np.random.randn(1000)

if __name__ == '__main__':
    dataframe = get_movie_dataframe()
    # print(dataframe.info())
    # a = dataframe.groupby('director')['util_num'].sum()
    # b = a.sort_values(ascending=False).head(10)
    # print(b)
    # comments_num_statistics = dataframe.groupby('movie_title')['comment_num']
    # comments_num_statistics = comments_num_statistics.sort_values(ascending=False).head(10)
    # comments_num_statistics = dataframe.sort_values('comment_num', ascending=False)[['movie_title', 'comment_num']].head(10)
    # print(comments_num_statistics)

    comment_df = get_comments_dataframe()
    # comment_df['comment_timestamp'] = comment_df['comment_timestamp'].str.slice(0, 7)
    # print(comment_df.head(1))
    # print(comment_df.groupby('commenter').apply(comment_df_year).head(1))

    # year_comment_df = comment_df.groupby('commenter').apply(comment_df_year)
    # year_comment_statistics = year_comment_df.groupby('comment_timestamp')['util_num'].sum()
    # year_comment_statistics = year_comment_statistics.sort_values(ascending=False).head(10)
    # print(year_comment_statistics)

    # month_comment_df = comment_df.groupby('commenter').apply(comment_df_month)
    # month_comment_statistics = month_comment_df.groupby('comment_timestamp')['util_num'].sum()
    # month_comment_statistics = month_comment_statistics.sort_values(ascending=False)
    # print(month_comment_statistics)

    day_comment_df = comment_df
    day_comment_statistics = day_comment_df.groupby('comment_timestamp')['util_num'].sum()
    day_comment_statistics = day_comment_statistics.sort_values(ascending=False).head(10)
    print(day_comment_statistics)