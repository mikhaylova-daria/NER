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

import nltk
import pandas
#from sklearn.metrics import classification_report, confusion_matrix
#from sklearn.preprocessing import LabelBinarizer
import nltk.stem.porter

from time import time

import argparse
import sys

import re
def get_shape(x):
    x = re.sub(r'([a-z]+)','x',x)
    x = re.sub(r'([A-Z]+)','X',x)
    x = re.sub(r'([0-9]+)','0',x)
    return x

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

stemmer = nltk.stem.porter.PorterStemmer()

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default=os.getcwd() + os.sep + 'Corpus')
paths = parser.parse_args(sys.argv[1:])

allfolders = os.listdir(paths.pathCorpus)
times = []

def addPosTag(folder):
    print folder
    articles = os.listdir(unicode(paths.pathCorpus+os.sep+folder))
    for i_article in articles:
        #t0 = time()
        article = open(paths.pathCorpus+os.sep+folder+os.sep+i_article+os.sep+"article")
        text = article.read().decode('utf-8')

        dfForArticle = pandas.read_csv(paths.pathCorpus+os.sep+folder+os.sep+i_article+os.sep+'features')
        postager = []
        l = 0
        sentences = nltk.tokenize.sent_tokenize(text)
        for sentence in sentences:
            sentence_list = nltk.tokenize.word_tokenize(sentence)
            pos_tag_list =  nltk.pos_tag(sentence_list)
            for pos_i, word in enumerate(sentence_list):
                postager.append(pos_tag_list[pos_i][1])
        del dfForArticle['id']
        dfForArticle.insert(11, 'PosTag', postager)
        dfForArticle.to_csv(path_or_buf=paths.pathCorpus+os.sep+folder+os.sep+i_article+os.sep+"features", index_label='id')
        #t1 = time()
        #print "Finish " + i_article + "time = %f" %(t1-t0)


import multiprocessing
pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
pool.map(addPosTag, allfolders)