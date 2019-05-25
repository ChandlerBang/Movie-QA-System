import pandas as pd
import pymysql
from py2neo import Graph,Node,Relationship
import csv

# 链接neo4j
test_graph = Graph(
    "http://localhost:7474",
    username="neo4j",
    password="jinwei"
)
# 清空数据库
test_graph.delete_all()

# 导入节点 电影类型  == 注意类型转换
cypher = '''LOAD CSV WITH HEADERS  FROM "file:///genre.csv" AS line \
            MERGE (p:Genre{gid:toInteger(line.genre_id),name:line.genre_name})'''
test_graph.run(cypher)

# 导入节点 演员信息
cypher = '''LOAD CSV WITH HEADERS FROM 'file:///person.csv' AS line
MERGE (p:Person { pid:toInteger(line.person_id)}) 
ON CREATE SET p.birth = line.person_birth_day, p.biography = line.person_biography
ON MATCH SET p.birth = line.person_birth_day, p.biography = line.person_biography
ON CREATE SET p.death = line.person_death_day,p.eng_name =line.person_english_name
ON MATCH SET p.death = line.person_death_day, p.eng_name =line.person_english_name
ON CREATE SET p.birthplace = line.birthplace, p.pname = line.person_name
ON MATCH SET p.birthplace = line.birthplace, p.pname = line.person_name
'''
test_graph.run(cypher)



#导入节点 电影信息
cypher = '''LOAD CSV WITH HEADERS  FROM "file:///movie.csv" AS line    
MERGE (p:Movie{mid:toInteger(line.movie_id),title:line.movie_title})
ON CREATE SET p.introduction = line.movie_introduction, p.movie_releasedate = line.movie_releasedate, p.rating=toFloat(line.movie_rating)
ON MATCH SET p.introduction = line.movie_introduction, p.movie_releasedate = line.movie_releasedate, p.rating=toFloat(line.movie_rating)
'''
test_graph.run(cypher)

## 导入关系 actedin  电影是谁参演的 1对多
cypher = '''LOAD CSV WITH HEADERS FROM "file:///person_to_movie.csv" AS line   
match (from:Person{pid:toInteger(line.person_id)}),(to:Movie{mid:toInteger(line.movie_id)})    
merge (from)-[r:actedin{pid:toInteger(line.person_id),mid:toInteger(line.movie_id)}]->(to)  
'''
test_graph.run(cypher)


# 导入关系  电影是什么类型 == 1对多
cypher = '''LOAD CSV WITH HEADERS FROM "file:///movie_to_genre.csv" AS line  
match (from:Movie{mid:toInteger(line.movie_id)}),(to:Genre{gid:toInteger(line.genre_id)})    
merge (from)-[r:is{mid:toInteger(line.movie_id),gid:toInteger(line.genre_id)}]->(to)  
'''
test_graph.run(cypher)


# 查询relationship的语句
cypher = "match (n)-[r:actedin]-(b) return n,r,b limit 10"
test_graph.run(cypher)

"""
-- 问：章子怡都演了哪些电影？  
match(n:Person)-[:actedin]->(m:Movie) where n.pname='章子怡' return m.title  
  
--  删除所有的节点及关系  
MATCH (n)-[r]-(b)  
DELETE n,r,b  
"""