__author__ = 'daria'
'''Save features in features.txt
format:

id Word   Offset    typeNE   feature1 feature2 feature3 ...
0  word1   0        Person
1  word2   13       Location
2  word3   24       0
...

'''
import os
import sys

import pandas
import numpy as np
import nltk

article = open("article")
text = article.read().decode('utf-8')

if os.path.exists("train") is False:
    open(os.getcwd() + "/train", 'w')

dfForArticle = pandas.DataFrame()

'''for line in article:
    sentences = nltk.tokenize.sent_tokenize(line.decode('utf-8'))
    if os.path.exists("features") is False:
        f = open(os.getcwd() + "/features", 'w')
        f.close()
    for sentence in sentences:
        dfForSentence = pandas.DataFrame()
        dfForSentence.insert(0, 'Word', nltk.tokenize.word_tokenize(sentence.encode('utf-8')))
        dfForArticle = dfForArticle.append(dfForSentence, ignore_index=True)
    #print line
    #print dfForArticle
'''


words = []
offset = []
l = 0

for q in nltk.tokenize.word_tokenize(text):
    #unknown Anton's kostul'
    if q == '\ufeff':
        continue
    words.append(q.encode('utf-8'))
    pos = text.find(q, l)
    offset.append(pos)
    l = max(len(q) + pos, l)

dfForArticle.insert(0, 'Word', words)
dfForArticle.insert(1, 'Offset', offset)


import json
def read_json(path_to_json):
    with open(path_to_json) as json_file:
        json_of_article = json.load(json_file)
    return json_of_article

from collections import OrderedDict
def get_entities(json_of_article):
    entities = dict([])
    for j in json_of_article:
        if len(j) == 0:
            continue
        s = (j['Type'])
        for pair in j['Boundaries']:
            entities[pair[0]] = list([pair[1], s ])
    entities = OrderedDict(sorted(entities.items(), key=lambda t:t[0]))
    return entities

json_of_article = read_json("res.json")
entities_offset = get_entities(json_of_article)

entities_type = []

i=0
last=0
last_type = "No"
for x in entities_offset.keys():
    while offset[i]<x:
        if offset[i] < last and offset[i] >= 0:
            entities_type.append(last_type)
        else:
            entities_type.append("No")
        i += 1
    if offset[i] == x:
        entities_type.append(entities_offset[x][1])
        last = entities_offset[x][0]
        last_type = entities_offset[x][1]
        i += 1
    else:
        print "Ooooops strange"


while i<len(offset):
    if offset[i] < last and offset[i] >= 0:
        entities_type.append(last_type)
    else:
        entities_type.append("No")
    i += 1

dfForArticle.insert(2, 'TypeNE', entities_type)

dfForArticle.to_csv(path_or_buf="./features", index_label="id")
