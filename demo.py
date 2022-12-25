import json
import random
import time
import re

from get_patent_num import get_patent_num
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import datetime
from cnt_num import conn_ali_report_2

# patent = []
# with open('demo.txt', 'r', encoding='utf-8') as f:
#     read = f.readline()
#     while read:
#         patent.append(read.strip('\n'))
#         read = f.readline()

sql = """insert into `company_patent_cited`(`publication_num`,`cited_count`,`cited_by`,`create_time`) values (%s, %s, %s, %s)"""

while True:
    
    date_first = datetime.datetime.now().strftime('%Y%m%d')
    patent = None
    while not patent:
        try:
            patent = get_patent_num()[0]
        except Exception as e:
            print('获取公开号产生错误！', e)
    with open('time.txt', 'w', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'))
    with open('need/{}.jsonl'.format(date_first), 'w', encoding='utf-8') as f:
        for patent_num in patent:
            f.write(patent_num)
            f.write('\n')
    print('共读取到%s条数据！' % len(patent), 'date:', datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'))
    del patent
    url = "https://patents.glgoo.top/patent/{}/en?oq={}"
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    brower = webdriver.Chrome(options=chrome_options)

    index = 1
    with open('need/{}.jsonl'.format(date_first), 'r', encoding='utf-8') as f1:
        patent_num = f1.readline()[:-1]
        while patent_num:
            try:
                date = datetime.datetime.now().strftime('%Y%m%d')

                try:
                    brower.get(url.format(patent_num, patent_num))
                except Exception as e:
                    print(e)
                    patent_num = f1.readline()[:-1]
                    continue
                time.sleep(random.random() + 1)
                js = "return document.body.scrollHeight"
                # 获取滚动条的高度
                new_height = brower.execute_script(js)
                for i in range(0, new_height, 300):
                    time.sleep(0.05)
                    brower.execute_script('window.scrollTo(0, %s)' % i)

                time.sleep(random.random() + 1)

                # 判断谷歌有没有收录这个专利
                is_404 = re.findall('<title>Error 404 \(Not Found\)!!1</title>', brower.page_source)
                if is_404:
                    # with open('error/{}.jsonl'.format(date), 'a', encoding='utf-8') as f:
                    #     f.write(json.dumps({'num': patent_num, 'info': '404,谷歌未收录该专利!'}))
                    #     f.write('\n')
                    print(index, patent_num, '404,谷歌未收录该专利!')
                    index += 1
                    patent_num = f1.readline()[:-1]
                    continue
                # 获取该文章有没有被引用
                isCited = re.findall('<dl class="links style-scope patent-result">[\s\S]+?</dl>', brower.page_source)[0] \
                    if re.findall('<dl class="links style-scope patent-result">[\s\S]+?</dl>', brower.page_source) else ""
                isCited = re.sub(r'<.+?>', '', isCited).replace('\n', '')

                retry_count = 1
                while not len(isCited) and retry_count <= 5:  # 再取5次
                    # input("断点：isCited为空。41")
                    print("isCited为空,retry_count:%s" % retry_count)
                    time.sleep(random.random() + 2 ** retry_count)
                    brower.get(url.format(patent_num, patent_num))
                    time.sleep(random.random() + 1)
                    new_height = brower.execute_script(js)
                    for i in range(0, new_height, 300):
                        time.sleep(0.05)
                        brower.execute_script('window.scrollTo(0, %s)' % i)
                    time.sleep(random.random() + 1)
                    # 重新获取该文章有没有被引用
                    isCited = re.findall('<dl class="links style-scope patent-result">[\s\S]+?</dl>', brower.page_source)[0] \
                        if re.findall('<dl class="links style-scope patent-result">[\s\S]+?</dl>', brower.page_source) else ""
                    isCited = re.sub(r'<.+?>', '', isCited).replace('\n', '')
                    retry_count += 1

                if 'Cited by' not in isCited and len(isCited) > 0:
                    content = {'patent_num': patent_num, 'cited_count': 0, 'cited_by': []}
                    # with open('res/{}.jsonl'.format(date), 'a', encoding='utf-8') as f:
                    #     json.dump(content, f, ensure_ascii=False)
                    #     f.write('\n')
                    content['create_'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    content['cited_by'] = ','.join(content['cited_by'])
                    info = [item for item in content.values()]

                    print(index, content, conn_ali_report_2(sql, info))

                if 'Cited by' in isCited:  # 有被引用
                    # 获取引用数量
                    cited_by_num = re.findall('Cited by \(.+?\)', isCited)[0]
                    cited_by_num = re.findall('\(.+?\)', cited_by_num)[0]
                    cited_by_num = cited_by_num.strip('()')

                    html = re.findall(r'<h3\sid="citedBy"[\s\S]*?<h3', brower.page_source)
                    # # 再取一遍
                    # if not html:  # 没找到
                    #     input('断点：娶不到引用部分html。68')
                    #     time.sleep(random.random() + 3)
                    #     brower.get(url.format(patent_num, patent_num))
                    #     time.sleep(random.random() + 1)
                    #     new_height = brower.execute_script(js)
                    #     for i in range(0, new_height, 300):
                    #         time.sleep(0.05)
                    #         brower.execute_script('window.scrollTo(0, %s)' % i)
                    #
                    #     time.sleep(random.random() + 1)
                    #     html = re.findall(r'<h3\sid="citedBy"[\s\S]*?<h3', brower.page_source)

                    if html:  # 找到引用段落
                        html = html[0]
                        xml = etree.HTML(html)
                        patent_list = xml.xpath('//*[@id="link"]')
                        patent_list = list(map(lambda x: x.text, patent_list))
                        if len(patent_list) == int(cited_by_num):
                            content = {'patent_num': patent_num, 'cited_count': len(patent_list), 'cited_by': patent_list}
                            # with open('res/{}.jsonl'.format(date), 'a', encoding='utf-8') as f:
                            #     json.dump(content, f, ensure_ascii=False)
                            #     f.write('\n')
                            content['create_'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            content['cited_by'] = ','.join(content['cited_by'])
                            info = [item for item in content.values()]
                            print(index, content, conn_ali_report_2(sql, info))

                        else:
                            # input('断点：爬取引用数量不对。92')
                            content = {'patent_num': patent_num, 'error': '被引用数量爬取错误！'}

                            with open('error/{}.html'.format(patent_num), 'w', encoding='utf-8') as f:
                                f.write(brower.page_source)
                            print(index, content, "爬取失败！！！")

                    else:  # 重新找了一次还是没找到
                        content = {'patent_num': patent_num}
                        with open('error/{}.html'.format(patent_num), 'w', encoding='utf-8') as f:
                            f.write(brower.page_source)
                        print(index, content, "爬取失败！！！")

                index += 1
                patent_num = f1.readline()[:-1]
            except Exception as e:
                print('最外层try，except,系统产生未知错误！', e)
                patent_num = f1.readline()[:-1]
                brower = webdriver.Chrome(options=chrome_options)
