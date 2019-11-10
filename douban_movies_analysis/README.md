# TOP250 豆瓣电影分析

## 安装

使用了 numpy,pandas,wordcloud 等库，可根据TOP250_douban_movies文件夹下的requirements.txt安装

```shell
pip3 install -r requirements.txt
```

## 结构说明

util 文件夹下是一些 util 的函数方法；
data 文件夹下是停用词表文件；font 文件夹下是词云所用的字体文件；
cloud_imgs 文件夹有 genre_clouds 和 movie_clouds 两个文件夹，分别用来存放根据电影名称和电影类型生成的短评的词云图片；
analysis 文件夹下有 statistics 和 DeepLearning 两个文件夹，statistics 文件夹下是对爬虫数据进行统计分析的函数，DeepLearning 文件夹下是通过深度学习对短评等数据进行统计分析的函数。

## 运行

运行前一定确保已经已经运行过TOP250_douban_movies 中的爬虫程序，因为分析程序需要使用数据库中爬取的数据。具体方法，可自行查看statistics 文件夹下的分析文件。