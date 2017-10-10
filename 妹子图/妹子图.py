# _*_coding: utf-8_*_
import os
import asyncio
from random import randint
from functools import wraps
from time import perf_counter

import aiohttp
import aiofiles
from scrapy import Selector
"""
-------------------------------------------------
   File Name：     妹子图
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
        print('{cls_name} spend time: {time:.8f}'.format(cls_name=cls_name, time=end_time - start_time))
        return result
    return wrapper


class MeiZiTuDownload:
    def __init__(self, *, genre: str='cute'):
        self.base_url = 'http://www.meizitu.com/a/{genre}_{page_num}.html'
        self.genre = genre
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    async def get_html_content(self, url: str):
        """
        :param url: 网页的url地址
        :return:    网页的html源码
        """
        req = await aiohttp.request('GET', url, headers=self.headers)
        content = await req.read()
        content = content.decode('gbk')
        return content

    async def get_page_item(self, page_num: int):
        """
        :param page_num: 获取网页中的每一页中的具体的url地址
        :return:
        """
        item_url = self.base_url.format(genre=self.genre, page_num=page_num)
        content = await self.get_html_content(item_url)
        selector = Selector(text=content)
        urls = list(set(selector.css('#maincontent a::attr(href)').extract()))
        page_items = (url for url in urls if url.startswith('http://www.meizitu.com/a/'))
        for item in page_items:
            await self.get_item(item)

    async def get_item(self, item: str):
        """
        :param item: 单独的下载页面
        :return:
        """
        item_content = await self.get_html_content(item)
        selector = Selector(text=item_content)
        dir_name = selector.css('#maincontent div.metaRight h2 a::text').extract_first()
        if not dir_name:
            dir_name = ''.join(chr(randint(97, 122)) for _ in range(1, 10))
        image_urls = selector.css('#picture p img::attr(src)').extract()
        if not image_urls:
            image_urls = selector.css('.postContent p img::attr(src)').extract()
        'ok' if os.path.exists(dir_name) else os.mkdir(dir_name)
        for image_url in image_urls:
            image_name = image_url.rsplit('/', 1)[-1]
            save_path = os.path.join(dir_name, image_name)
            await self.download_images(save_path, image_url)

    async def download_images(self, save_path: str, image_url: str):
        """
        :param save_path: 保存图片的路径
        :param image_url: 图片的下载的url地址
        :return:
        """
        req = await aiohttp.request('GET', image_url, headers=self.headers)
        image = await req.read()
        fp = await aiofiles.open(save_path, 'wb')
        await fp.write(image)

    async def __call__(self, page_num: int):
        await self.get_page_item(page_num)

    def __repr__(self):
        cls_name = type(self).__name__
        return '{cls_name}{args}'.format(cls_name=cls_name, args=self.genre)


if __name__ == "__main__":
    start = perf_counter()
    download = MeiZiTuDownload(genre='fuli')
    loop = asyncio.get_event_loop()
    to_do = [download(num) for num in range(1, 4)]
    wait_future = asyncio.wait(to_do)
    resp, _ = loop.run_until_complete(wait_future)
    loop.close()
    end = perf_counter()
    func_name = download.__class__.__name__
    spend_time = end - start
    print(format('end', '*^100'))
    print('{func_name} spend time: {time:.5f}'.format(func_name=func_name, time=spend_time))
