from __future__ import division, print_function
from matplotlib import pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np

from utils.utils import get_commenters_dataframe, locaP, locaC, geod_world, geod_china

dataframe = get_commenters_dataframe()


def df_preprocess():
    dataframe['province'] = dataframe.location.apply(locaP)
    dataframe.province.fillna('oversea', inplace=True)
    dataframe['country'] = dataframe.location.apply(lambda x: x.split(sep=',')[-1].strip()) \
        .apply(locaC)
    dataframe.country.fillna('China', inplace=True)


def plot_follow():
    matplotlib.rc('figure', figsize=(14, 7))
    matplotlib.rc('font', size=14)
    matplotlib.rc('axes', grid=False)
    matplotlib.rc('axes', facecolor='white')

    sns.jointplot(x="follower_num", y="following_num", data=dataframe)
    plt.savefig('follow_analysis.jpg')
    plt.show()


def province_followers():
    temp = (dataframe.groupby(by='province').sum().follower_num / dataframe.province.value_counts()).sort_values(
        ascending=False).reset_index()
    print(temp.head(10))


def province_following():
    temp = (dataframe.groupby(by='province').sum().following_num / dataframe.province.value_counts()).sort_values(
        ascending=False).reset_index()
    print(temp.head(10))


def commenter_country_analysis():
    temp = dataframe.country.value_counts().reset_index()

    df = pd.DataFrame({'NAME': temp['index'].tolist(), 'NUM': (np.log1p(temp['country']) + 10).tolist()})
    geod_world(df, 'Where the brief comment comes from around world? ', )

    plt.savefig('commenter_country_analysis.jpg')
    plt.show()

    print(temp.head(10))


def commenter_province_analysis():
    temp = dataframe.province.value_counts().reset_index()

    df = pd.DataFrame({'NAME': temp['index'].tolist(), 'NUM': (np.log1p(temp['province'])).tolist()})
    geod_china(df, 'Where the brief comment comes from in China? ', legend=False)

    plt.savefig('commenter_province_analysis.jpg')
    plt.show()

    print(temp.head(10))


if __name__ == '__main__':
    df_preprocess()
    # plot_follow()
    # commenter_province_analysis()
    # commenter_country_analysis()
    # province_followers()
    # province_following()
