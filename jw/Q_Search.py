# -*- coding: utf-8 -*-

import jw.svm_model as svm_model
from py2neo import Graph,Node,Relationship
from jw.svm_model import test
import fool

test_graph = Graph(
    "http://118.25.74.160/",
    port= 7474,
    username="neo4j",
    password="jinwei"
)


def q_type_0(entities):
    cypher = """match(m:Movie) where m.title='{}' return m.rating  """.format(entities[1])
    res = test_graph.run(cypher).data()[0]
    #print(res['m.rating'])
    return str(res['m.rating'])


def q_type_2(entities):
    cypher = """match(m:Movie)-[:is]->(g:Genre) where m.title='{}' return g  """.format(entities[1])
    res = test_graph.run(cypher).data()
    answer = ""
    for x in res:
        answer+=str(x['g']['name'])+","
     #   print(x['g']['name'])
    return answer+'\n'


def q_type_3(entities):
    cypher = """match(m:Movie) where m.title='{}' return m.introduction  """.format(entities[1])
    res = test_graph.run(cypher).data()[0]
    answer = str(res['m.introduction'])
    #print(res['m.introduction'])
    return answer+"\n"


def q_type_4(entities):
    cypher = """match(n:Person)-[:actedin]->(m:Movie) where m.title='{}' return n  """.format(entities[1])
    res = test_graph.run(cypher).data()
    answer = ""
    for p in res:
        if  p['n']['pname']:
            answer += str(p['n']['pname'])+","
     #       print(p['n']['pname'], end=", ")
        else:
            answer += str(p['n']['eng_name']) + ","
    #        print(p['n']['eng_name'], end=", ")
   # print("\n")
    return answer+'\n'


def q_type_5(entities):
    cypher = """match (n:Person) where n.pname="{}" return n""".format(entities[0])
    res = test_graph.run(cypher).data()[0]
    answer = ""
    if(res['n']['biography']):
  #      print(res['n']['biography'])
        answer+=str(res['n']['biography'])+'\n'
    else:
        for x in res['n']:
 #           print(x, ":", res['n'][x])
            answer += str(x)+":"+str(res['n'][x])+'\n'
    return answer


def q_type_7(entities):
    cypher = """match(n:Person)-[:actedin]->(m:Movie) where n.pname='{}' return m  """.format(entities[0])
    res = test_graph.run(cypher).data()
    answer = ""
    for p in res:
#        print(p['m']['title'],end=', ')
        answer+=str(p['m']['title'])+', '
    # print("\n")
    return answer+'\n'

def get_query_type(query):

    q_type, entities = test(query)
    # print(q_type)
    try:
        answer = solution_dict[q_type](entities)
    except:
        answer = "Sorry...I don't know this answer TAT ..."
    return entities, answer


solution_dict = {0: q_type_0, 2:q_type_2, 3:q_type_3, 4:q_type_4, 5:q_type_5, 7:q_type_7}

if __name__=="__main__":
    while(1):
        try:
            get_query_type()
        except:
            get_query_type()
            #print("~~~Bing: 5555555~")