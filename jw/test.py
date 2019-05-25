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

cypher = """match (n:Person) where n.pname="{}" return n""".format("巩俐")
res = test_graph.run(cypher).data()[0]
for x in res['n']:
    print(x, ":",res['n'][x])

# 查询relationship的语句
cypher = "match (n)-[r:actedin]-(b) return n,r,b limit 10"
print(test_graph.run(cypher).data())

"""
-- 问：章子怡都演了哪些电影？  
match(n:Person)-[:actedin]->(m:Movie) where n.pname='章子怡' return m.title  
"""