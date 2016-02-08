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
    if pos < 0:
        pos = 0
    offset.append(pos)
    l = len(q) + pos

dfForArticle.insert(0, 'Word', words)
dfForArticle.insert(1, 'Offset', offset)

dfForArticle.to_csv(path_or_buf="./features", index_label="id")