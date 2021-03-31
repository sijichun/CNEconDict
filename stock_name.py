#!/usr/bin/python3

import tushare
import os
import sys
import requests
from bs4 import BeautifulSoup
import time
import random
from functions import errlog
from functions import remove_duplicates
import csv


def get_stock_names(code, retry=3):
    """
    从新浪财经中爬去上市公司的名称以及简称。
    需要的输入：
    code: 股票代码
    retry：错误发生之后重新尝试的次数
    """
    stock_info = {'code': code}
    URL = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/%s.phtml"
    url = URL % code
    for i in range(retry):
        try:
            html = requests.get(url, timeout=10).content.decode('gb18030')
            bs = BeautifulSoup(html, "html.parser")
            table = bs.find_all(name="table", attrs={"id": "comInfo1"})[0]
            tds = table.find_all(name="td")
            last_key = None
            key_list = ["公司名称：", "证券简称更名历史："]
            for td in tds:
                if last_key is None and td.text in key_list:
                    last_key = td.text
                elif last_key is not None:
                    stock_info[last_key] = td.text
                    last_key = None
            if "公司名称：" in stock_info and "证券简称更名历史：" in stock_info:
                break
        except Exception as e:
            print("stock_name错误：" + str(e) + "：" + url + "：函数get_stock_names")
            errlog("stock_name错误：" + str(e) + "：" + url + "：函数get_stock_names")
            time.sleep(random.random() * 10 + i * 10)
    if "证券简称更名历史：" in stock_info:
        stock_info["证券简称更名历史："] = stock_info["证券简称更名历史："].replace(
            "*",
            "").replace("（", "").replace("）", " ").replace("(", " ").replace(
                ")", " ").replace("  ", " ").strip().split(' ')
    else:
        stock_info = None
    return stock_info


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
    ## get the current path
    PWD = os.path.dirname(os.path.realpath(__file__))
    SUB_PATH = PWD + '/sub_dics'
    Dic_File = SUB_PATH + "/stock_name.txt"
    Csv_File = SUB_PATH + "/stock_name.csv"
    if os.path.exists(SUB_PATH) is not True:
        os.mkdir(SUB_PATH)
    if Need_Craw:
        ## 先使用TuShare获取股票列表
        data = tushare.get_stock_basics()
        Stock_Codes = [c for c in data.index]
        Stock_Names = [
            n.replace(" ", "").replace("*", "").strip() for n in data['name']
        ]
        Stock_Indus = set([i for i in data['industry']])
        ## 写入industry
        with open(SUB_PATH + "/indus_name.txt", 'a') as f:
            for i in Stock_Indus:
                f.write(str(i) + '\n')
        ## 重新读入文件，删除重复
        with open(SUB_PATH + "/indus_name.txt", 'r') as f:
            content = f.readlines()
        content = list(set(content))
        with open(SUB_PATH + "/indus_name.txt", 'w') as f:
            f.writelines(content)
        ## 接下来使用新浪财经获取更加详细的名称列表
        ## 开始爬虫
        stock_info_csv = []
        i = 0
        for code, name in zip(Stock_Codes, Stock_Names):
            stock_info = get_stock_names(code)
            if stock_info is not None:
                stock_info['证券简称更名历史：'].append(name)
                stock_info['公司简称：'] = stock_info['公司名称：'].replace(
                    "股份有限公司", "").replace("有限责任公司", "")
                with open(Dic_File, 'a') as f:
                    f.write(stock_info['公司名称：'] + "\n")
                    f.write(stock_info['公司简称：'] + "\n")
                    for n in stock_info['证券简称更名历史：']:
                        f.write(n + '\n')
                        if 'A' in n or 'B' in n or 'G' in n or 'N' in n:
                            f.write(
                                n.replace('A', '').replace('B', '').replace(
                                    'G', '').replace('N', '') + '\n')
                stock_info['证券简称更名历史：'] = ' '.join(stock_info['证券简称更名历史：'])
                stock_info_csv.append(stock_info)
            i += 1
            print("%s/%s" % (i, len(Stock_Codes)), stock_info)
            time.sleep(10 + random.random() * 10)
        ## 重新读入文件，删除重复
        remove_duplicates(Dic_File)
        ## 写入csv文件
        csv_exist = os.path.exists(Csv_File)
        with open(Csv_File, 'a') as f:
            header = ['code', '公司名称：', '公司简称：', '证券简称更名历史：']
            f_csv = csv.DictWriter(f, header)
            if not csv_exist:
                f_csv.writeheader()
            f_csv.writerows(stock_info_csv)
        remove_duplicates(Csv_File, csv=True)
    else:
        from functions import getdic
        getdic("stock_name.txt")
        print("Complete 1/2. See ./sub_dics/stock_name.txt")
        getdic("indus_name.txt")
        print("Complete 2/2. See ./sub_dics/indus_name.txt")