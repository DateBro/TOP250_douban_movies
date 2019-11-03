#! /bin/bash
cd /home/zhiyong/pycharm_projects/TPO250_douban_movies/
n=1
while (( $n <= 26 ))
do
    echo $n
    (( n++ ))
    scrapy crawl comments >> movie_comments.log 2>&1 &
    sleep 2400
done