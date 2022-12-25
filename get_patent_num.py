# -*- coding: UTF-8 –*-
import datetime
import json
import pymysql
import requests



def conn_ali_report(sql):
    # 链接
    # conn = pymysql.connect(host='127.0.0.1', user='root', password='SW_MySQL_231',port=22936, database='Report',charset='utf8')  # 与数据库的服务端建立连接，databases是我们要查询的表所在的数据库
    conn = pymysql.connect(host='120.27.209.14', user='qingyang', password='qingyang.suwen', port=22936,
                           database='Report',
                           charset='utf8')  # 与数据库的服务端建立连接，databases是我们要查询的表所在的数据库

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()

    try:
        # 执行sql语句
        line = cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
        result = cursor.fetchall()

    except Exception as e:
        print(e)
        # 如果发生错误则回滚
        # logger.error(e)
        conn.rollback()
        conn.close()
        return None, None

    # 关闭数据库连接
    conn.close()
    return result, line

def get_from_before():
    with open('page_num.txt', 'r', encoding='utf-8') as f:
        page = f.readline()

    response = requests.get('http://120.27.209.14:7105/report/get_patent_num?page=%s&page_size=10000' % page)

    with open('page_num.txt', 'w', encoding='utf-8') as f:
        f.write(str(int(page) + 1))

    response = json.loads(response.text)
    patent_num_list = []
    for item in response['data']:
        if item['num']:
            patent_num_list.append(item['num'])
    return patent_num_list

def get_patent_num():
    try:
        response = requests.get('http://120.27.209.14:22912/get_patent_num')
        response = json.loads(response.text)
        patent_num_list = response['data']
        patent_num_count = response['count']
        if patent_num_count < 10000:
            patent_num_list = get_from_before()
            patent_num_count = len(patent_num_list)
    except:
        patent_num_list = get_from_before()
        patent_num_count = len(patent_num_list)
        
    return patent_num_list, patent_num_count


if __name__ == '__main__':
    print(get_patent_num())
