import json
import math
import os
import re

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.ncbi.nlm.nih.gov/pubmed/"

# 爬取文章内容时的展示格式，可选的report值有：docsum/abstract/medline/xml/uilist
DEFAULT_PARAM = {
    'report': 'medline',
    'format': 'text',
}
REQUEST_HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",  # noqa
}


def query(record_name, default='Mesh Terms', current=1, pagesize=200):
    """
    查询关键词，并开始爬取数据

    """
    print('初始化处理', record_name)
    total = get_total_count(record_name, default=default, current=current, pagesize=pagesize)
    print('总数:', total)
    for i in range(1, math.ceil(total / pagesize) + 1):
        deal_page(record_name, default, current=i, pagesize=pagesize)


def get_total_count(record_name, default='Mesh Terms', current=1, pagesize=200):
    """
    获取该关键词搜索得到的总数

    """

    term = '%s[%s]' % (record_name, default)
    resp = requests.post(BASE_URL, headers=REQUEST_HEADERS, data={
        'term': term,
        'EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_Pager.CurrPage': current,
        'EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_DisplayBar.PageSize': pagesize
    })

    soup = BeautifulSoup(resp.text, 'html.parser')
    result = soup.find(name='h3', class_='result_count left').string
    # 如果有数据，result展示为'Items: 1 to 200 of 54822'， 如果没有数据，则展示为'Items: 0'，因此只要判断字符串中是否有'of'即可
    has_entry = result.find('of')
    if has_entry == -1:
        return 0
    else:
        total = int(result[has_entry + 3:])
        return total


def deal_page(record_name, default='Mesh Terms', current=1, pagesize=200):
    """
    爬取当前分页里的数据

    """
    print('开始处理第', current, '页', '每页', pagesize, '条')

    term = '%s[%s]' % (record_name, default)
    resp = requests.post(BASE_URL, headers=REQUEST_HEADERS, data={
        'term': term,
        'EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_Pager.CurrPage': current,
        'EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_DisplayBar.PageSize': pagesize
    })

    # 获取每一页文章列表的PMID
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = soup.find_all(name='dd')
    pmid_list = []
    if results:
        for i in results:
            pmid_list.append(i.string)

    # 对每一个PMID爬取文章详情
    for pmid in pmid_list:
        get_content(pmid, record_name, DEFAULT_PARAM)


def get_content(pmid, save_dir, params):
    """
    爬取pmid对应的文章，并将页面body内容保存到以pmid为名的文件中，同一个record_name检索出来的所有文章都存放在record_name为名的文件夹中

    save_dir: 保存路径
    params: 页面参数

    """
    resp = requests.get(BASE_URL + pmid, params)
    if not os.path.exists('./crawler/pubmed-details/' + save_dir):
        os.mkdir('./crawler/pubmed-details/' + save_dir)

    # 参数中有format时，获取<pre></pre>中，当参数仅有report且只在['abstract', 'docsum']中时，获取<body></body>中的信息
    if params['format'] and params['report'] in ['medline', 'xml', 'docsum', 'abstract', 'uilist']:
        result = re.search('<pre>[\d\D]*</pre>', resp.text)
        content = result.group().replace('<pre>', '').replace('</pre>', '')
    elif params['report'] in ['abstract', 'docsum'] and not params['format']:
        result = re.search('<body>[\d\D]*</body>', resp.text)
        content = result.group().replace('<body>', '').replace('</body>', '')
    else:
        content = resp.text.strip()

    file_name = './crawler/pubmed-details/' + save_dir + '/' + pmid + '.txt'
    with open(file_name, 'w') as f:
        f.write(content)
    print('已经将结果写入到', file_name)


with open('./crawler/unique-id-mesh.txt', 'r') as f:
    for line in f:
        item = json.loads(line)
        query(item.get('RecordName'))
