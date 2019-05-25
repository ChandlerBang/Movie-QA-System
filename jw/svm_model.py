# -*- coding: utf-8 -*-
from sklearn.svm import SVC
import fool
from jw.config import opt
import os
import numpy as np
import re
import pickle

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


def word2vec(line):               
    word2id_list = [0]*len(vocab_dict)
    entities = {} 
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

    for word in fool.cut(line)[0]:
    # for word in list(jieba.cut(line)):
        try:
            word2id_list[int(vocab_dict[word])] = 1
        except:
            pass
    return word2id_list, entities



def read_templates(folder):
    fs = os.listdir(folder)
    pattern = re.compile(r'\d+') 
    data = []
    labels = []
    for file in fs:
        tmp_path = os.path.join(folder, file)
        f = open(tmp_path, 'r', encoding="utf-8_sig")
        for line in f.readlines():
            line = word2vec(line.strip())
            data.append(line)
            labels.append(int(pattern.findall(file)[0])) 
        #label = np.array(label).transpose()

    return data, labels

def train():
    train_data, train_labels = read_templates(opt.template_folder)
    model = SVC(kernel='linear', probability=True)
    model.fit(train_data, train_labels)
    with open(opt.svm_checkpoint, 'wb') as outfile:
        pickle.dump(model, outfile)
    print('Saved classifier model to file "%s"' % opt.svm_checkpoint)

def test(query):
    query_vec, entities = word2vec(query)
    predictions = model.predict_proba([query_vec])
    predictions = np.array(predictions)
    q_type_pred = np.argmax(predictions, axis=1)
    return q_type_pred[0], entities

if __name__ =="__main__":
    print('Testing classifier')


