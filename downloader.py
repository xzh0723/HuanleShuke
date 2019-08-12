# -*- coding: utf-8 -*-
# @Time    : 2019/7/1 12:53
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : downloader.py
# @Software: PyCharm

import requests
import os
from bs4 import BeautifulSoup
from decrypter import decrypter


class Downloader:

    def __init__(self, nover_id):
        self.novel_id = nover_id
        self.url = f'https://www.ciweimao.com/book/{self.novel_id}'
        self.headers = {
            'Cookie': 'UM_distinctid=16a5f891d93780-0e39d24b77661f-7a1b34-100200-16a5f891d94772; CNZZDATA1276028418=1408790198-1556378705-null%7C1561954856; get_task_type_sign=1; ci_session=nnkdhueoa232goc60s23g36bu614d8fd; readPage_visits=4; Hm_lvt_1dbadbc80ffab52435c688db7b756e3a=1561903572,1561908781,1561954957,1561956665; Hm_lpvt_1dbadbc80ffab52435c688db7b756e3a=1561956731; user_id=1489563; reader_id=1489563; login_token=74c819e64a095f23eb2e871adabc420a',
            'Host': 'www.ciweimao.com',
            'Referer': 'https://www.ciweimao.com/rank-index/favor-total',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }

    def save_to_txt(self, novel_name, chapter_name, chapter_content):
        path = os.path.abspath('...')
        save_path = path + '\\' + novel_name
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            print(f'{novel_name} 小说文件夹创建成功!')
        chapter = save_path + '\\' + chapter_name + '.txt'
        with open(chapter, 'w') as f:
            f.write(chapter_content)

    def run(self):
        r = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        nover_info = {
            'name': soup.select('.title')[0].get_text(),
            'author': soup.select('.book-info h3 span a')[0].string,
            'words_num': soup.find('p', {'class': "book-grade"}).find_all('b')[2].get_text(),
            'introduction': soup.select('.book-intro-cnt div')[0].get_text()
        }
        print(nover_info)
        nover_name = nover_info['name']
        chapter_lists = soup.select('.book-chapter-list')
        for chapter_list in chapter_lists:
            chapters = chapter_list.find_all('li')
            for chapter in chapters:
                chapter_id = chapter.find('a')['href'].split('/')[-1]
                chapter_name = chapter.find('a').string
                spider = decrypter(chapter_id)
                chapter_content = spider.run()
                try:
                    self.save_to_txt(nover_name, chapter_name, chapter_content)
                    print(f'章节{chapter_name} 下载成功!')
                except Exception as e:
                    print(f'章节{chapter_name} 下载失败!')
                    print(e.args)


if __name__ == '__main__':
    novel_id = input('请输入小说ID>> ')
    spider = Downloader(novel_id)
    spider.run()
