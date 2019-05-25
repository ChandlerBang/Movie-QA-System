# coding=utf-8
from flask import Flask, jsonify, render_template, request
from py2neo import Graph
import jw.Q_Search as search
import json
import logging


logging.basicConfig(level=logging.WARNING,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='logs/pro2.log',
                filemode='a')

app = Flask(__name__)
graph = Graph(
    "http://118.25.74.160/",
    port= 7474,
    username="neo4j",
    password="jinwei"
)

f = open("recommend_list.json","r")
d = json.loads(f.read())
f.close()
def buildNodes_g(nodeRecord):
    data = {"id": str(nodeRecord['g']['gid']), "name": str(nodeRecord['g']['name']),"label":"Genre"}

    return {"data": data}


def buildNodes_m(nodeRecord):
    data = {"id": str(nodeRecord['m']['mid']), "name": str(nodeRecord['m']['title']), "label":"Movie"}

    return {"data": data}


def buildNodes_p(nodeRecord):
    data = {"id": str(nodeRecord['n']['pid']),
            "name": str(nodeRecord['n']['pname']) if nodeRecord['n']['pname']!=None else nodeRecord['n']['eng_name'],
            "label":"Person"}

    return {"data": data}

def buildEdges(relationRecord):
    data = {"source": str(relationRecord['r']['mid']),
            "target": str(relationRecord['r']['gid']),
            "relationship": relationRecord['r']._Relationship__type}

    return {"data": data}

def buildEdges_act(relationRecord):
    data = {"source": str(relationRecord['r']['pid']),
            "target": str(relationRecord['r']['mid']),
            "relationship": relationRecord['r']._Relationship__type}
    return {"data": data}

def get_recommendation(entities):
    try:
        q = list(entities.values())[0]
        print(q)
        global d
        return d[q]
    except:
        return "周星驰, 葛优, 巩俐, 冯小刚</div><div>功夫, 十面埋伏, 霸王别姬, 黄飞鸿"
        
@app.route('/')
def hello_world():
    logging.warning("====== user ip: {} ======".format(request.remote_addr))
    return render_template('index000.html')

@app.route('/search', methods=['GET'])
def index1():
    return render_template('index1.html')

@app.route('/search', methods=['POST'])
def index2():
    query = request.form['Search']
    logging.warning("====== Query: {} ======".format(query))
    #query = query.replace("\n","")
    global entities

    entities,answer = search.get_query_type(query)
    f = open("./templates/index2.html", 'w',encoding="utf-8")
    message_front ='''<!DOCTYPE html>
<html>
<head>
    <title>Knowledge Graph</title>
    <link href="/static/css/style.css" rel="stylesheet" />
    <script src="http://cdn.bootcss.com/jquery/1.11.2/jquery.min.js"></script>
    <script src="http://cdn.bootcss.com/cytoscape/2.3.16/cytoscape.min.js"></script>
    <script src="/static/js/code.js"></script>
</head>
<body>'''
    question = '<h3>Your Question</h3>\n<div>'+str(query).replace('\n','')+ '</div>\n'
    recommendation = '<h3>You Might Like this</h3><div>'+get_recommendation(entities)+'</div>'
    answer = '<h3>Answer</h3>\n<div>' + str(answer).replace('\n','<br>') + "</div>\n"
    message_back='''<h3>Movie Graph</h3>
  <div id="cy"></div>
</body>
</html>'''
    f.write(message_front+question+answer+recommendation+message_back)
    f.close()
    return render_template('index2.html')

@app.route('/graph')
def get_graph():
    try:
        nodes = list(map(buildNodes_m, graph.run('''MATCH (n:Person)-[:actedin]->(m:Movie) where n.pname='{}' RETURN m'''.format(entities[0]))))
        nodes = nodes+list(map(buildNodes_p, graph.run('''MATCH (n:Person)-[:actedin]->(m:Movie) where n.pname='{}' RETURN n'''.format(entities[0]))))
        edges = list(map(buildEdges_act, graph.run('''MATCH (n:Person)-[r]->(m:Movie) where n.pname='{}' RETURN r limit 100'''.format(entities[0]))))
    except:
        try:
            nodes = list(map(buildNodes_m, graph.run(
                '''MATCH (n:Person)-[:actedin]->(m:Movie) where m.title='{}' RETURN m'''.format(entities[1]))))
            nodes = nodes+list(map(buildNodes_p, graph.run(
                '''MATCH (n:Person)-[:actedin]->(m:Movie) where m.title='{}' RETURN n limit 100'''.format(entities[1]))))
            nodes = nodes + list(map(buildNodes_g, graph.run(
                '''MATCH (m:Movie)-[:is]->(g:Genre) where m.title="{}"  RETURN g'''.format(entities[1]))))
            edges = list(map(buildEdges_act, graph.run(
                '''MATCH (n:Person)-[r]->(m:Movie) where m.title='{}' RETURN r limit 100'''.format(entities[1]))))
            edges = edges + list(map(buildEdges, graph.run(
                '''MATCH (m:Movie)-[r]->(g:Genre) where m.title="{}"  RETURN r limit 100'''.format(entities[1]))))
        except:
            #print("=============Here is OK=============")
            nodes = list(map(buildNodes_m, graph.run(
                '''MATCH (m:Movie)-[:is]->() where m.title="2046" or m.title= "Qin Yong" or m.mid=146 or m.mid=53281 RETURN m''')))
            nodes = nodes + list(map(buildNodes_g, graph.run(
                '''MATCH (m:Movie)-[:is]->(g:Genre) where m.title="2046" or m.title= "Qin Yong" or m.mid=146 or m.mid=53281  RETURN g''')))
            nodes = nodes + list(map(buildNodes_p, graph.run(
                '''MATCH (n:Person)-[r]->(m:Movie) where m.title="2046" or m.title= "Qin Yong" or m.mid=146  or m.mid=53281 RETURN n''')))
            edges = list(map(buildEdges, graph.run(
                '''MATCH (m:Movie)-[r]->(g:Genre) where m.title="2046" or m.title= "Qin Yong" or m.mid=146  or m.mid=53281 RETURN r limit 100''')))
            edges = edges + list(map(buildEdges_act, graph.run(
                '''MATCH (n:Person)-[r]->(m:Movie) where m.title="2046" or m.title= "Qin Yong" or m.mid=146  or m.mid=53281 RETURN r limit 100''')))
            #print("=============Here is OK=============")
            # nodes = map(buildNodes, graph.cypher.execute('MATCH (n) RETURN n'))
            # edges = map(buildEdges, graph.cypher.execute('MATCH ()-[r]->() RETURN r'))

    return jsonify(elements = {"nodes": nodes, "edges":edges})  
if __name__ == '__main__':
    app.run(debug = True)