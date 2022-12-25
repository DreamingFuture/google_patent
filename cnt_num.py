import datetime
import json
import os
import time
from pip import main
import pymysql


def get_conn():
    try:
        conn = pymysql.connect(host='rm-bp17j89w23w92l4r2so.mysql.rds.aliyuncs.com', user='qingyang',
                               password='SWqingyang123', port=3306, database='report',
                               charset='utf8', write_timeout=120)  # 与数据库的服务端建立连接，databases是我们要查询的表所在的数据库
        return conn
    except Exception as e:
        print('reconnect', e)
        time.sleep(1)
        return None


def conn_ali_report_2(sql, data):
    # 链接
    conn = None
    while not conn:
        conn = get_conn()

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    line = 0
    try:
        # 执行sql语句
        line = cursor.execute(sql, data)
        # 提交到数据库执行
        conn.commit()
        result = cursor.fetchall()
    except Exception as e:
        # 如果发生错误则回滚
        print(e)
        # logger.error(e)
        conn.rollback()
        conn.close()
        return None, None

    # 关闭数据库连接
    conn.close()
    return line

if __name__ == '__main__':
    path = 'res/'
    file_list = os.listdir(path)
    print(file_list)
    cnt = 0
    for file_name in file_list:
        index = 1
        sql = """insert into `company_patent_cited`(`publication_num`,`cited_count`,`cited_by`,`create_time`) values (%s, %s, %s, %s)"""
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open('res/' + file_name, 'r', encoding='utf-8') as f:
            data = f.readline()
            while data:
                data = json.loads(data)
                if index > 0:
                    data['create_'] = date
                    data['cited_by'] = ','.join(data['cited_by'])
                    info = [item for item in data.values()]
                    # for item in data.values():
                    #     info.append(item)
                    print(file_name, ' : ', index, conn_ali_report_2(sql, info))
                index += 1
                data = f.readline()