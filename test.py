# -*- coding: utf-8 -*-
from sklearn.svm import SVC
from jw.config import opt
import os
import numpy as np
import re
import pickle
import fool
from jw.utils import person_names, movie_names,genre_names

import warnings
warnings.filterwarnings('ignore')

with open(opt.svm_checkpoint, 'rb') as infile:
    model = pickle.load(infile)
print('Loaded classifier model from file "%s"' % opt.svm_checkpoint)


vocab_dict = {}
with open(opt.vocab_file, "r", encoding="utf-8_sig") as f:
    for line in f.readlines():
        id, word = line.strip().split(":")
        # if word not in opt.stop_words:
        vocab_dict[word] = id

def word2vec(line):               # 把word转换成词向量，不在vocab_dict中的word置为0    是否需要过滤Stopwords？
    word2id_list = [0]*len(vocab_dict)
    entities = {} #用来存这些实体
    for x in person_names:
        if x in line:
            line = line.replace(x," nnt ")
            entities[0] = x
    for x in movie_names:
        if x in line:
            line = line.replace(x," nm ")
            entities[1] = x
    for x in genre_names:
        if x in line:
            line = line.replace(x," ng ")
            entities[2] = x
    words, ner = fool.analysis(line)
    for entity in ner[0]:
        if(entity[2]=="person"or entity[2]=="company"):
            line = line.replace(entity[3]," nnt ")
