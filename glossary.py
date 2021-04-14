#!/usr/bin/python3

import os
import sys
import requests
from bs4 import BeautifulSoup
import time
import random
from functions import errlog
from functions import remove_duplicates
import csv
from queue import Queue

glossary = []
tasks = Queue()
Iterm_sets = set()

## get the current path
PWD = os.path.dirname(os.path.realpath(__file__))
SUB_PATH = PWD + '/sub_dics'
Dic_File = SUB_PATH + "/glossary.txt"
Csv_File = SUB_PATH + "/glossary.csv"
if os.path.exists(SUB_PATH) is not True:
    os.mkdir(SUB_PATH)


def get_glossary_sub_page(retry=3):
    """
    从Queue中挨个取出元素并爬取
    """
    URL = "https://wiki.mbalib.com%s"
    while not tasks.empty():
        father_iterm = tasks.get()
        for i in range(retry):
            try:
                if "https://" not in father_iterm['link']:
                    url = URL % father_iterm['link']
                html = requests.get(url, timeout=10).text
                # print(html)
                bs = BeautifulSoup(html, "html.parser")
                ## 获取所有子类
                links = bs.find_all(name="a")
                for l in links:
                    href = l.get('href')
                    if href != None and href.find(
                            "Category:") > 0 and l.text[-2:] not in ('标志',
                                                                     '图像'):
                        if l.text not in Iterm_sets:
                            iterm = {
                                'iterm': l.text,
                                'link': href,
                                'father': father_iterm['iterm'],
                                'tag': 'Category'
                            }
                            glossary.append(iterm)
                            tasks.put(iterm)
                            Iterm_sets.add(l.text)
                            with open(Dic_File, 'a') as f:
                                f.write(l.text + '\n')
                            print(iterm)
                ## 获取所有词语列表
                div = bs.find_all(name="div", attrs={"class": "page_ul"})[0]
                links = div.find_all(name='a')
                for l in links:
                    href = l.get('href')
                    if href != None and href.find("/wiki/") == 0:
                        if l.text not in Iterm_sets:
                            iterm = {
                                'iterm': l.text,
                                'link': href,
                                'father': father_iterm['iterm'],
                                'tag': 'Iterm'
                            }
                            glossary.append(iterm)
                            Iterm_sets.add(l.text)
                            with open(Dic_File, 'a') as f:
                                f.write(l.text + '\n')
                            print(iterm)
                break
            except Exception as e:
                print("glossary错误：" + str(e) + "：" + url +
                      "：函数get_glossary_sub_page")
                errlog("glossary错误：" + str(e) + "：" + url +
                       "：函数get_glossary_sub_page")
                os.system("pppoe-stop; pppoe-start")
                time.sleep(random.random() * 10 + i * 10)
        time.sleep(3 + 10 * random.random())
    return


def get_glossary(retry=3):
    """
    从MBA智库百科中爬取专业词汇。
    """
    URL = "https://wiki.mbalib.com%s"
    url = URL % "/wiki/MBA智库百科:分类索引"
    for i in range(retry):
        try:
            html = requests.get(url, timeout=10).text
            bs = BeautifulSoup(html, "html.parser")
            links = bs.find_all(name="a")
            for l in links:
                href = l.get('href')
                if href != None and href.find(
                        "Category:") > 0 and l.text[-2:] not in ('标志', '图像'):
                    if l.text not in Iterm_sets:
                        iterm = {
                            'iterm': l.text,
                            'link': href,
                            'father': 'ROOT',
                            'tag': 'Category'
                        }
                        glossary.append(iterm)
                        tasks.put(iterm)
                        Iterm_sets.add(l.text)
                        with open(Dic_File, 'a') as f:
                            f.write(l.text + '\n')
                        print(iterm)
            break
        except Exception as e:
            print("glossary错误：" + str(e) + "：" + url + "：函数get_glossary")
            errlog("glossary错误：" + str(e) + "：" + url + "：函数get_glossary")
            os.system("pppoe-stop; pppoe-start")
            time.sleep(random.random() * 10 + i * 10)
    ## 开始爬取子页面
    get_glossary_sub_page(retry=retry)
    return


if __name__ == "__main__":
    ## 获取命令行参数
    Need_Craw = False
    args = sys.argv[1:]
    for arg in args:
        if arg == "-update":
            Need_Craw = True
        else:
            print("无效的参数：" + arg)
            sys.exit(1)

    if Need_Craw:
        ## 从网络爬取
        get_glossary()
        ## 写入文件
        remove_duplicates(Dic_File)
        ## 写入csv文件
        csv_exist = os.path.exists(Csv_File)
        with open(Csv_File, 'a') as f:
            header = ['iterm', 'link', 'father', 'tag']
            f_csv = csv.DictWriter(f, header)
            if not csv_exist:
                f_csv.writeheader()
            f_csv.writerows(glossary)
    else:
        from functions import getdic
        getdic("glossary.txt")
        print("Complete. See ./sub_dics/glossary.txt")