# coding=utf-8
from flask import Flask, jsonify, render_template, request
from py2neo import Graph


import json
import numpy as np


app = Flask(__name__)
graph = Graph(
    "http://118.25.74.160/",
    port= 7474,
    username="neo4j",
    password="jinwei"
)

results = graph.run('''MATCH (m:Movie)-[r]->(g:Genre) where m.title="黄飞鸿"  RETURN r limit 100''')
print(len(results))