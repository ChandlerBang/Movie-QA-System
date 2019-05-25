# -*- coding: utf-8 -*-
#import pymysql
import json

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


def write_movie_names(filename):
    with open(filename, 'w', encoding='gbk') as f:
        conn = get_conn()
        cur = conn.cursor()
        sql = "select movie_title from movie"
        cur.execute(sql)
        results = cur.fetchall()
        for x in results:
            f.write((x[0])+'\n')

def get_movie_names(filename):
    with open(filename,'r',encoding='utf-8') as f:
        for line in f.readlines():
            print((line))

def write_movie_names1(filename):
    conn = get_conn()
    cur = conn.cursor()
    sql = "select movie_title from movie"
    cur.execute(sql)
    results = cur.fetchall()
    results = [x[0] for x in results]
    res_js = json.dumps(results)  
    f = open(filename, 'w')
    f.write(res_js)
    f.close()

def get_movie_names1(filename):
    f = open(filename, 'r')
    movie_names = json.loads(f.read())  # loads: Convert a string to a dictionary
    # for x in movie_names:
    #     print(x)
    print(len(movie_names))
    f.close()
    return movie_names

def write_person_names(filename):
    conn = get_conn()
    cur = conn.cursor()
    sql = "select person_name from person"
    cur.execute(sql)
    results = cur.fetchall()
    results = [x[0] for x in results if x[0]!=None]
    res_js = json.dumps(results)  # 
    f = open(filename, 'w')
    f.write(res_js)
    f.close()

def get_person_names(filename):
    f = open(filename, 'r')
    person_names = json.loads(f.read())  # loads: Convert a string to a dictionary
    # for x in person_names:
    #     print(x)
    print(len(person_names))
    f.close()
    return person_names


movie_names = get_movie_names1("./jw/movies.json")
person_names = get_person_names("./jw/person_names.json")

def get_genre_names(filename):
    f = open(filename, 'r')
    person_names = json.loads(f.read())  # loads: Convert a string to a dictionary
    # for x in person_names:
    #     print(x)
    print(len(person_names))
    f.close()
    return person_names

genre_names = get_genre_names("./jw/genres.json")
if __name__ == "__main__":
    # write_movie_names("./movies.txt")
    # get_movie_names("./movies.txt")
    #write_movie_names1("./movies.json")
    get_movie_names1("./movies.json")
    #write_person_names("./person_names.json")
    get_person_names("./person_names.json")
    pass
