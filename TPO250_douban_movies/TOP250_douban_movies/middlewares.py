import json
import logging
import time
import cv2
import requests
import random
import numpy as np
import os
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger
from selenium.webdriver import ActionChains

class SeleniumMiddleware():
    def __init__(self, timeout=None, service_args=[]):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser = webdriver.PhantomJS(service_args=service_args)
        self.browser.maximize_window()
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)
        self.username = '13455792425'
        self.password = 'doubanzhl'

    def __del__(self):
        self.browser.close()

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

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   service_args=crawler.settings.get('PHANTOMJS_SERVICE_ARGS'))

    # 下面都是之前CookiePool中用来破解验证码的代码
    # 已改
    def open(self, login_url):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.get(login_url)

        # 先点击密码登录
        password_login_button = self.browser.find_element_by_xpath('//*[@id="account"]/div[2]/div[2]/div/div[1]/ul[1]/li[2]')
        self.webdriverwait_click(self.browser, password_login_button)

        # 先输入账号和密码
        account_input = self.browser.find_element_by_xpath('//*[@id="username"]')
        password_input = self.browser.find_element_by_xpath('//*[@id="password"]')

        account_input.send_keys(self.username)
        password_input.send_keys(self.password)

        # 找到登录按钮（豆瓣html里不是button，而是一个像button的链接）
        login_button = self.browser.find_element_by_xpath("//*[@id='account']/div[2]/div[2]/div/div[2]/div[1]/div[4]/a")
        self.webdriverwait_click(self.browser, login_button)
        time.sleep(2)

    @staticmethod
    def webdriverwait_click(dri, element):
        """
        显示等待 click
        :param dri: driver
        :param element:
        :return:
        """
        WebDriverWait(dri, 10, 5).until(lambda dr: element).click()

    # 已改
    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#account > div.login-wrap > div.login-right > div > div.account-tabcon-start > div.account-form > div.account-form-error > span'), '用户名或密码错误'))
        except TimeoutException:
            return False

    # 已改完
    def login_successfully(self):
        """
        判断是否登录成功
        :return:
        """
        try:
            return bool(
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="db-global-nav"]/div/div[1]/ul/li[2]/a'))))
        except TimeoutException:
            return False

    @staticmethod
    def get_postion(chunk, canves):
        """
        判断缺口位置
        :param chunk: 缺口图片是原图
        :param canves:
        :return: 位置 x, y
        """
        otemp = chunk
        oblk = canves
        target = cv2.imread(otemp, 0)
        template = cv2.imread(oblk, 0)
        # w, h = target.shape[::-1]
        temp = 'temp.jpg'
        targ = 'targ.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        template = cv2.imread(temp)
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        return x, y

    @staticmethod
    def get_track(distance):
        """
        模拟轨迹 假装是人在操作
        :param distance:
        :return:
        """
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
            else:
                a = -random.randint(3, 5)  # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    @staticmethod
    def urllib_download(imgurl, imgsavepath):
        from urllib.request import urlretrieve
        urlretrieve(imgurl, imgsavepath)

    # 已改，试试效果
    def login_with_auth(self):
        driver = self.browser

        # 出现验证码之后
        driver.switch_to.frame(driver.find_element_by_id('tcaptcha_popup'))  # switch 到 滑块frame
        time.sleep(0.5)
        # 带缺口的大图
        bk_block = driver.find_element_by_css_selector('#slideBkg')
        web_image_width = bk_block.size
        web_image_width = web_image_width['width']
        bk_block_x = bk_block.location['x']

        # 缺口图
        slide_block = driver.find_element_by_css_selector('#slideBlock')
        slide_block_x = slide_block.location['x']

        bk_block = driver.find_element_by_css_selector('#slideBkg').get_attribute('src')       # 大图 url
        slide_block = driver.find_element_by_css_selector('#slideBlock').get_attribute('src')  # 小滑块 图片url
        slide_button = driver.find_element_by_css_selector('#tcaptcha_drag_button')

        os.makedirs('./image/', exist_ok=True)
        self.urllib_download(bk_block, './image/bkBlock.png')
        self.urllib_download(slide_block, './image/slideBlock.png')
        time.sleep(0.5)

        img_bkblock = Image.open('./image/bkBlock.png')
        real_width = img_bkblock.size[0]
        width_scale = float(real_width) / float(web_image_width)
        position = self.get_postion('./image/bkBlock.png', './image/slideBlock.png')
        real_position = position[1] / width_scale
        real_position = real_position - (slide_block_x - bk_block_x)
        track_list = self.get_track(real_position + 4)

        ActionChains(driver).click_and_hold(on_element=slide_button).perform()  # 点击鼠标左键，按住不放
        time.sleep(0.2)

        # print('第二步,拖动元素')
        for track in track_list:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
            time.sleep(0.002)
        # 看一下微调的效果如何
        ActionChains(driver).move_by_offset(xoffset=-random.randint(0, 1), yoffset=0).perform()   # 微调，根据实际情况微调
        time.sleep(1)
        # print('第三步,释放鼠标')
        ActionChains(driver).release(on_element=slide_button).perform()
        time.sleep(1)

        print('滑动验证码破解成功')


# 为了反爬虫就先不用代理池了，感觉多个ip用同一个账号更容易被检测...
class ProxyMiddleware():
    def __init__(self, proxy_url):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                self.logger.debug('使用代理 ' + proxy)
                request.meta['proxy'] = uri

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            proxy_url=settings.get('PROXY_URL')
        )


class CookiesMiddleware():
    def __init__(self, cookies_url):
        self.logger = logging.getLogger(__name__)
        self.cookies_url = cookies_url

    def get_random_cookies(self):
        try:
            response = requests.get(self.cookies_url)
            if response.status_code == 200:
                cookies = json.loads(response.text)
                return cookies
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        self.logger.debug('正在获取Cookies')
        cookies = self.get_random_cookies()
        if cookies:
            self.logger.debug('已获得Cookies')
            request.cookies = cookies
            # 打印这个的话信息太多容易看不到关键信息
            # self.logger.debug('使用Cookies ' + json.dumps(cookies))

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            cookies_url=settings.get('COOKIES_URL')
        )


class RandomUserAgentMiddleware():
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/603.2.5 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.5",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.0 Mobile/14F89 Safari/602.1",
            "Mozilla/5.0 (Windows NT 6.1; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.2.5 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.5",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36 OPR/46.0.2597.32",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/59.0.3071.109 Chrome/59.0.3071.109 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 OPR/45.0.2552.898",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 OPR/46.0.2597.39",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
        ]

    def process_request(self, request, spider):
        # request.headers['User-Agent'] = random.choice(self.user_agents)
        request.headers['Connection'] = 'close'

    def process_response(self, request, response, spider):
        response.status = 201
        return response
