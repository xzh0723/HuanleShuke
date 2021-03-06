# -*- coding: utf-8 -*-
# @Time    : 2019/8/12 20:15
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : decrypter.py
# @Software: PyCharm


import requests
import execjs
import asyncio
import re
import json
from pyppeteer import launch
from bs4 import BeautifulSoup


class decrypter():
    def __init__(self, chapter_id):
        self.chapter_id = chapter_id
        self.headers = {
            'Cookie': 'UM_distinctid=16a5f891d93780-0e39d24b77661f-7a1b34-100200-16a5f891d94772; Hm_lvt_1dbadbc80ffab52435c688db7b756e3a=1561896349; get_task_type_sign=1; CNZZDATA1276028418=1408790198-1556378705-null%7C1561897010; ci_session=4a2klr4a4svb6h3okn6p6o2erqrb5tmj; Hm_lpvt_1dbadbc80ffab52435c688db7b756e3a=1561902251; readPage_visits=8; user_id=3144512; reader_id=3144512; login_token=e0e7eb16e3b4f75dbfe89ac7ed23a354',
            'Host': 'www.ciweimao.com',
            'Origin': 'https://www.ciweimao.com',
            'Referer': 'https://www.ciweimao.com/chapter/102927393',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.access_key = self.get_access_key()

    def get_access_key(self):
        url = 'https://www.ciweimao.com/chapter/ajax_get_session_code'
        data = {
            'chapter_id': self.chapter_id
        }
        r = requests.post(url, data=data, headers=self.headers).json()
        if r['code'] == 100000:
            access_key = r['chapter_access_key']
            return access_key
        else:
            print('Something wrong!')

    def get_encrypt_content(self):
        url = 'https://www.ciweimao.com/chapter/get_book_chapter_detail_info'
        data = {
            'chapter_id': self.chapter_id,
            'chapter_access_key': self.access_key
        }
        r = requests.post(url, data=data, headers=self.headers).json()
        if r['code'] == 100000:
            return {
                'accessKey': self.access_key,
                'content': r['chapter_content'],
                'keys': r['encryt_keys']
            }
        else:
            print('Something wrong!')

    def update_html(self, encrypt_content):
        with open('欢乐书客.html', 'rb') as f:
            html = f.read().decode()
        params = re.search('var params = (.*?);', html, re.S).group(0)
        # print(params)
        html_ = html.replace(params, 'var params = ' + json.dumps(encrypt_content) + ';')
        with open('欢乐书客.html', 'wb') as f:
            f.write(html_.encode())

    async def decrypt_(self):
        browser = await launch({'args': ['--no-sandbxo', '--disable-infobars', ]}, userDataDir=r'D:\拉勾\userdata')
        page = await browser.newPage()
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36')
        await page.setJavaScriptEnabled(enabled=True)
        await page.goto('file:///D:/%E6%AC%A2%E4%B9%90%E4%B9%A6%E5%AE%A2/%E6%AC%A2%E4%B9%90%E4%B9%A6%E5%AE%A2.html')
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        paragraphs = soup.find_all('p', {'class': 'chapter'})
        chapter_content = ''
        for paragraph in paragraphs:
            paragraph_content = paragraph.string
            chapter_content += paragraph_content + '\n'
        await browser.close()
        return chapter_content

    def run(self):
        encrypt_content = self.get_encrypt_content()
        self.update_html(encrypt_content)
        loop = asyncio.get_event_loop()
        chapter_content = loop.run_until_complete(self.decrypt_())
        return chapter_content

    def decrypt(self):
        # 直接运行那段js报错CryptoJS net defined, 懒得去琢磨怎么改, 直接用浏览器运行了
        with open('decrypt.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        content = ctx.call('decrypt', self.get_encrypt_content())
        soup = BeautifulSoup(content, 'lxml')
        chapter_content = soup.get_text()
        print(chapter_content)


if __name__ == '__main__':
    spider = decrypter("100110997")
    spider.run()
