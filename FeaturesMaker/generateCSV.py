__author__ = 'daria'
'''Save features in features.txt
format:

id Word   Offset    typeNE   pos_in_sent feature2 feature3 ...
0  word1   0        Person       0
1  word2   13       Location     1
2  word3   24       0            2
...

'''
import os
import sys

import pandas
import numpy as np
import nltk

from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
import nltk.stem.porter

stemmer=nltk.stem.porter.PorterStemmer()

article = open("article")
text = article.read().decode('utf-8')


dfForArticle = pandas.DataFrame()


words = []
offset = []
pos_in_sent = []
stem = []
last_two = []
last_three = []
isupper = []
istitle = []
isdigit = []

l = 0
sentences = nltk.tokenize.sent_tokenize(text)


for sentence in sentences:
    sentence_list = nltk.tokenize.word_tokenize(sentence)
    for pos_i, word in enumerate(sentence_list):
        #unknown Anton's kostul'
        if word == '\ufeff':
            continue
        words.append(word.encode('utf-8'))
        pos = text.find(word, l)
        offset.append(pos)
        l = max(len(word) + pos, l)

        pos_in_sent.append(pos_i)

        stem.append(stemmer.stem(word).encode('utf-8')),
        last_two.append(word[-3:].encode('utf-8')),
        last_three.append(word[-2:].encode('utf-8')),
        isupper.append(word.isupper()),
        istitle.append(word.istitle()),
        isdigit.append(word.isdigit()),



dfForArticle.insert(0, 'Word', words)
dfForArticle.insert(1, 'Offset', offset)
dfForArticle.insert(2, 'Pos_in_sent', pos_in_sent)
dfForArticle.insert(3, 'Stem', stem)
dfForArticle.insert(4, 'LastTwo', last_two)
dfForArticle.insert(5, 'LastThree', last_three)
dfForArticle.insert(6, 'IsUpper', isupper)
dfForArticle.insert(7, 'IsTitle', istitle)
dfForArticle.insert(8, 'IsDigit', isdigit)

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

i = 0
last = 0
last_type = "No"
for x in entities_offset.keys():
    while offset[i] < x:
        if offset[i] < last and offset[i] >= 0:
            entities_type.append(last_type.strip())
        else:
            entities_type.append("No")
        i += 1
    if offset[i] == x:
        entities_type.append(entities_offset[x][1].strip())
        last = entities_offset[x][0]
        last_type = entities_offset[x][1]
        i += 1
    else:
        print "Ooooops strange"


while i < len(offset):
    if offset[i] < last and offset[i] >= 0:
        entities_type.append(last_type.strip())

    else:
        entities_type.append("No")
    i += 1

print entities_type
dfForArticle.insert(2, 'TypeNE', entities_type)

dfForArticle.to_csv(path_or_buf=os.getcwd() + os.sep + "features", index_label="id")
