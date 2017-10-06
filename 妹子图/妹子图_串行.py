# _*_coding: utf-8_*_
import os
from time import perf_counter
from functools import wraps

import requests
from scrapy import Selector
"""
-------------------------------------------------
   File Name：     妹子图_串行
   Description :
   Author :        demon
   date：          06/10/2017
-------------------------------------------------
   Change Activity:
                   06/10/2017:
-------------------------------------------------
"""
__author__ = 'demon'


def timer(func):
    """
    :param func: 装饰器的函数，记录方法所消耗的时间
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        cls_name = func.__name__
        fmt = '{cls_name} {args} spend time: {time:.5f}'
        print(fmt.format(cls_name=cls_name, args=args, time=end_time - start_time))
        return result
    return wrapper


def get_content_css(url):
    req = requests.get(url)
    content = req.content.decode('gbk')
    selector = Selector(text=content)
    return selector


def get_page_items(*, start_page_num: int=1, end_page_num: int=2, step: int=1):
    items = []
    for page_num in range(start_page_num, end_page_num, step):
        base_url = 'http://www.meizitu.com/a/{genre}_{page_num}.html'
        selector = get_content_css(base_url.format(genre='cute', page_num=page_num))
        item_urls = list(set(selector.css('#maincontent a::attr(href)').extract()))
        items.extend(url for url in item_urls if url.startswith('http://www.meizitu.com/a/'))
    return items


def get_images(item):
    selector = get_content_css(item)
    image_urls = list(set(selector.css('#maincontent p img::attr(src)').extract()))
    dir_name = selector.css('#maincontent div.metaRight h2 a::text').extract_first()
    'ok' if os.path.exists(dir_name) else os.mkdir(dir_name)
    for url in image_urls:
        download_image(dir_name, url)


@timer
def download_image(dir_name, image_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    req = requests.get(image_url, headers=headers)
    image = req.content
    filename = image_url.rsplit('/', 1)[-1]
    save_path = os.path.join(dir_name, filename)
    with open(save_path, 'wb') as f:
        f.write(image)


if __name__ == "__main__":
    start = perf_counter()
    for item in get_page_items():
        get_images(item)
    end = perf_counter()
    print(format('end', '*^100'))
    print('download all images cost time:{:.3f}'.format(end - start))