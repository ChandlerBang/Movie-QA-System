# -*- coding: utf-8 -*-
import pymysql
import csv
import codecs

def get_conn():
    conn = pymysql.connect(
    host="localhost",
    database="movie",
    user="root",
    password="jinwei",
    # port=3306,
    charset='utf8',
    use_unicode=True,
    )
    return conn

def read_mysql_to_csv(filename, table):
    with codecs.open(filename=filename, mode='w', encoding='utf-8') as f:
        write = csv.writer(f, dialect='excel')
        conn = get_conn()
        cur = conn.cursor()

        sql = "select column_name from information_schema.columns where table_name='{}'".format(table)
        cur.execute(sql)
        results = cur.fetchall()
        col_names = []
        for x in results:
            col_names.append(x[0])
        write.writerow(col_names)

        sql = 'select * from {}'.format(table)
        cur.execute(sql)
        results = cur.fetchall()

        for result in results:
            print(result)
            write.writerow(result)

if __name__ == '__main__':
    for x in ["genre", "movie","movie_to_genre", "person", "person_to_movie"]:
        read_mysql_to_csv('{}.csv'.format(x), x)