# TOP250 豆瓣电影爬虫

## 安装

使用了 scrapy，selenium 等库，具体安装过程可参考《Python3爬虫开发实战》中的安装教程；

或者直接使用 requirements.txt

```
pip3 install -r requirements.txt
```

但 PhantomJs 无法用 pip 直接安装，具体安装过程可参考《Python3爬虫开发实战》中的安装教程；

## 设置说明

```python
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure a delay for requests for the same website (default: 0)
# 为了防止被反爬虫检测出来，设置的DOWNLOAD_DELAY较大
DOWNLOAD_DELAY = 5

# Enable or disable downloader middlewares
# 最终只使用 SeleniumMiddleware，之前实现的CookieMiddleware等由于担心更容易被监测没有使用
DOWNLOADER_MIDDLEWARES = {
   # 'TOP250_douban_movies.middlewares.CookiesMiddleware': 554,
   'TOP250_douban_movies.middlewares.SeleniumMiddleware': 555,
   # 'TOP250_douban_movies.middlewares.ProxyMiddleware': 555,
   # 'TOP250_douban_movies.middlewares.RandomUserAgentMiddleware': 543,
}

# 对爬取的数据进行整理与存储
ITEM_PIPELINES = {
   'TOP250_douban_movies.pipelines.MongoPipeline': 300
}

# 如果是在本地爬虫将数据存到服务器上可以修改，否则不用修改
MONGO_URI = '127.0.0.1'

# MongoDB 数据库名称
MONGO_DATABASE = 'top_250_douban_movies_test'

# Selenium 放弃爬取的超时总时间
SELENIUM_TIMEOUT = 20

# 对 PhantomJs 的设置，可以加速爬虫
PHANTOMJS_SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

# CookiePool 和 ProxyPool 已弃用，所以注释掉
# COOKIES_URL = 'http://localhost:5000/douban/random'
#
# PROXY_URL = 'http://localhost:5555/random'

RETRY_HTTP_CODES = [401, 403, 408, 414, 500, 502, 503, 504]

# 为了保持日志文件的简洁,设置为 INFO
LOG_LEVEL = 'INFO'
```

## 文件说明

### pipeline.py

根据书上的示例只修改了 open_spider 和 process_item 方法

```python
# 因为在 process_item 中会根据不同的 Item 进行不同的查询防止爬取重复的信息，所以对不同的 collection 设置了不同的索引，毕竟最后爬取到的短评有 33 万多条，设置一下索引对速度还是有提升的
def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[TOP250MovieInfoItem.collection].create_index([('movie_link', pymongo.ASCENDING)])
        self.db[MovieInfoItem.collection].create_index([('movie_link', pymongo.ASCENDING)])
        self.db[CommentInfoItem.collection].create_index([('commenter_link', pymongo.ASCENDING), ('comment_page_link', pymongo.ASCENDING)])
        self.db[CommenterInfoItem.collection].create_index([('commenter_link', pymongo.ASCENDING)])

# process_item 主要是根据不同的 Item 进行查询是否重复和插入
def process_item(self, item, spider):
        if isinstance(item, TOP250MovieInfoItem):
            condition = {'movie_link': item.get('movie_link')}
        elif isinstance(item, MovieInfoItem):
            condition = {'comments_link': item.get('comments_link')}
        elif isinstance(item, CommentInfoItem):
            condition = {'commenter_link': item.get('commenter_link'),
                         'comment_page_link': item.get('comment_page_link')}
        elif isinstance(item, CommenterInfoItem):
            condition = {'commenter_link': item.get('commenter_link')}

        result = self.db[item.collection].find_one(condition)
        if result is None:
            self.db[item.collection].insert(dict(item))
        return item
```

### middleware.py

middleware 中只使用了 SeleniumMiddleware，其中大部分代码是破解模拟登录时破解滑动验证码，由于代码比较多，破解滑动验证码的具体代码请自行查看。

```python
def process_request(self, request, spider):
        self.logger.info('PhantomJS is Starting')
        try:
            self.browser.get(request.url)
            time.sleep(1)
            html = self.browser.page_source
            current_url = request.url

            try:
                need_login = self.browser.find_element_by_xpath('//*[@id="db-global-nav"]/div/div[1]/a')
                self.logger.info('需要登录')
                login_link = need_login.get_attribute('href')
                self.open(login_link)
                if self.password_error():
                    self.logger.info('用户名或密码错误')
                # 如果不需要验证码直接登录成功
                if self.login_successfully():
                    self.logger.info('不需要验证码直接登录成功')
                    # 登陆成功以后跳回原来的页面
                    self.browser.get(current_url)
                else:
                    # 需要验证码的情况下登录
                    self.login_with_auth()
                    if self.login_successfully():
                        self.logger.info('需要验证码的情况下登录成功')
                        # 登陆成功以后跳回原来的页面
                        self.browser.get(current_url)
                    elif self.password_error():
                        self.logger.info('需要验证码的情况下登录，用户名或密码错误')
                    else:
                        self.logger.info('需要验证码的情况下登录，登录失败')
            except NoSuchElementException:
                self.logger.info('现在不需要登录，所以找不到登录元素')

            # 需要让浏览器模拟随机滑动页面，模拟人的行为
            random_scroll_nums = random.randint(0, 1)
            for i in range(random_scroll_nums):
                random_scroll_distance1 = random.randint(200, 5000)
                js = 'var q=document.documentElement.scrollTop=' + str(random_scroll_distance1)
                self.browser.execute_script(js)
                time.sleep(0.3)
                random_scroll_distance2 = random.randint(200, 5000)
                js = 'var q=document.documentElement.scrollTop=' + str(random_scroll_distance2)
                self.browser.execute_script(js)
                time.sleep(0.3)

            random_sleep = random.uniform(0.2, 0.8)
            time.sleep(random_sleep)

            return HtmlResponse(url=request.url, body=html, request=request, encoding='utf-8',
                                status=200)
        except TimeoutException:
            self.logger.error('self.browser.get(request.url) happened TimeoutException')
            return HtmlResponse(url=request.url, status=500, request=request)
        except Exception:
            self.logger.error('self.browser.get(request.url) happened error')
            return HtmlResponse(url=request.url, status=500, request=request)
```

### douban_movies.py

主要就是构造 TOP250 排行榜每一页的链接，然后解析每一页的电影名和电影页链接，然后发出爬取电影页信息的 Request，之后利用 xpath 或者 pyquery 正常解析网页信息即可。

```python
def start_requests(self):
        base_url = 'https://movie.douban.com/top250?start=$&filter='
        for start in range(10):
            url = str.replace(base_url, '$', str(start * 25))
            self.logger.info(url)
            yield Request(url, callback=self.parse_top250)

def parse_top250(self, response):
        top250_movie_info_item = TOP250MovieInfoItem()
        html = response.text
        doc = pq(html)
        all_movies = doc('#content > div > div.article > ol > li > div > div.info')
        for movie in all_movies.items():
            sleep_time = random.uniform(0.5, 1)
            time.sleep(sleep_time)

            movie_link = movie('div.hd > a').attr('href')
            title = movie('div.hd > a > span.title').text()
            top250_movie_info_item['title'] = title
            top250_movie_info_item['movie_link'] = movie_link
            self.logger.info(top250_movie_info_item)
            yield top250_movie_info_item
            # 然后发出爬取每个 movie 的具体信息的 request
            self.logger.info(movie_link)
            yield Request(movie_link, callback=self.parse_movie_item)
```

### comments.py

短评的爬取过程和电影信息爬取略有不同，因为在爬取短评大约 40 分钟之后就会无法爬取，查看日志文件发现报错全是 Retry，估计是被检测到异常暂时不允许访问，所以写一个 shell 脚本，每隔 40 分钟启动一次爬虫，因为每次爬虫都是爬取几部电影的短评，所以在一个 txt 文件中写一个接下来要爬取的电影 index，一开始是 0，每次爬虫都会 +10，所以经过 25 次就能结束爬虫。具体爬取的思路和电影信息的爬虫差不多，请自行查看。

```python
def start_requests(self):
        # 每次都要读取这次要开始爬的电影的链接index
        with open('/home/zhiyong/data/next_link_num.txt', 'rt') as f:
            # with open('E:\PycharmProjects\some_data/next_link_num.txt', 'rt') as f:
            next_link_index = f.read()
            next_link_index = int(next_link_index)

        # 将后面开始读的电影索引 + 10 写入文件
        with open('/home/zhiyong/data/next_link_num.txt', 'wt') as f:
            # with open('E:\PycharmProjects\some_data/next_link_num.txt', 'wt') as f:
            new_next_link_index = next_link_index + 10
            f.write(str(new_next_link_index))

        # 后面可以加一个从数据库中读取已爬取的comment链接去重
        movie_link_list = self.get_movie_link_list()
        comment_page_link_list = self.get_comment_page_link_list()

        for index in range(next_link_index, new_next_link_index):
            if index >= 250:
                break
            movie_link = movie_link_list[index]
            time.sleep(3)

            # 分别爬取好评，中评，差评
            choices = ['h', 'm', 'l']
            for choice in choices:
                # 爬取每种评论之前先 sleep 一段时间
                every_type_comments_sleep = random.randint(2, 5)
                time.sleep(every_type_comments_sleep)

                comment_suffix = 'comments?start=$&limit=20&sort=new_score&status=P'
                real_comments_link = movie_link + comment_suffix
                if choice == 'h':
                    real_comments_link = real_comments_link + '&percent_type=h'
                elif choice == 'l':
                    real_comments_link = real_comments_link + '&percent_type=l'
                else:
                    real_comments_link = real_comments_link + '&percent_type=m'

                for start in range(25):
                    tmp_link = real_comments_link
                    request_comments_link = str.replace(tmp_link, '$', str(start * 20))
                    if request_comments_link not in comment_page_link_list:
                        # 然后可以爬取每个 movie 的短评信息
                        self.logger.info(request_comments_link)
                        yield Request(url=request_comments_link, callback=self.parse_comments)
                    else:
                        self.logger.info(request_comments_link)
                        self.logger.info('该链接已经爬取过')
```

### commenters.py

现阶段爬取评论者的问题主要是速度太慢，毕竟一个网页最多只有一个用户的信息，再就是爬取时间过长也容易遇到 Retry 的问题，打算后面考虑一下有没有什么弥补措施。

```python
def start_requests(self):
        commenter_link_list = self.get_commenter_link_list()
        crawled_commenter_link_list = self.get_crawled_commenter_link_list()

        for commenter_link in commenter_link_list:
            if commenter_link not in crawled_commenter_link_list:
                crawled_commenter_link_list.append(commenter_link)
                time.sleep(4)
                self.logger.info(commenter_link)
                yield Request(url=commenter_link, callback=self.parse_commenters)
```

评论者信息爬取过程和前面其他爬虫最大的不同就是解析网页时一些异常情况的处理，比如账号已注销，账号已被永久停用等...其他地方和前面的爬虫大同小异。

```python
def parse_commenters(self, response):
        commenter_info_item = CommenterInfoItem()

        commenter_link = response.xpath('//*[@id="db-usr-profile"]/div[2]/ul/li[1]/a/@href').extract()
        try:
            commenter_link = commenter_link[0]
        except IndexError:
            # 已经注销账号的用户会出错
            self.logger.info('该用户已经主动注销帐号')
            return

        commenter_info_item['commenter_link'] = commenter_link

        location = response.xpath('//*[@id="profile"]/div/div[2]/div[1]/div/a/text()').extract()
        if location is None:
            lcoation = '未知'
        else:
            try:
                location = location[0]
            except IndexError:
                lcoation = '未知'
        commenter_info_item['location'] = location

        register_timestamp = response.xpath('//*[@id="profile"]/div/div[2]/div[1]/div/div/text()[2]').extract()
        try:
            register_timestamp = register_timestamp[0]
            # 截取 xxxx-xx-xx 日期
            result = re.findall('(.*)加入', register_timestamp)
            register_timestamp = result[0]
            register_timestamp = register_timestamp[0:10]
        except IndexError:
            # 因为有的账号根据log查看后发现是被永久停用的，没法获取注册时间
            register_timestamp = datetime.date.today()

        commenter_info_item['register_timestamp'] = register_timestamp

        account_name = response.xpath('//*[@id="profile"]/div/div[2]/div[1]/div/div/text()[1]').extract()
        try:
            account_name = account_name[0]
            account_name = str.strip(account_name)
            commenter_info_item['account_name'] = account_name[0]
        except IndexError:
            # 这种情况是 依据用户管理细则，帐号已被永久停用。
            self.logger.info('该依据用户管理细则，帐号已被永久停用')
            return

        following_num = response.xpath('//*[@id="friend"]/h2/span/a/text()').extract()
        try:
            following_num = following_num[0]
            # 截取 成员xxx 中的数字
            commenter_info_item['following_num'] = following_num[2:]
        except IndexError:
            # 如果没有关注的人的话没有用户关注多少人，但会有被0人关注
            following_num = 0

        follower_num = response.xpath('//*[@id="content"]/div/div[2]/p[1]/a/text()').extract()
        follower_num = follower_num[0]
        result = re.findall("被(.*)人关注", follower_num)
        follower_num = result[0]
        commenter_info_item['follower_num'] = follower_num
        self.logger.info(commenter_info_item)
        yield commenter_info_item
```

### comments_spider.sh

在菜鸟教程和博客园看了一点 shell 的基础知识和教程写的脚本，大神可以尝试用一下 crontab 执行定时任务（看了半天没看懂咋用...）。

```shell
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
```

## 运行

直接在命令行执行命令即可：

先启动爬取电影信息的爬虫；

```shell
scrapy crawl douban_movies

# 或者后台执行，将输出重定向到日志文件中
nohup scrapy crawl douban_movies > douban_movies.log 2>&1 &
```

再启动爬取评论的爬虫（因为短评的网页链接需要根据数据库里的电影链接构造）;

```shell
scrapy crawl comments

# 或者后台执行，将输出重定向到日志文件中
nohup scrapy crawl comments > comments.log 2>&1 &
```

最后才可以爬取评论者的信息；

```python
scrapy crawl commenters

# 或者后台执行，将输出重定向到日志文件中
nohup scrapy crawl commenters > commenters.log 2>&1 &
```