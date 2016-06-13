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
len_sent = open('len_sent', 'w')
for folder in allfolders:
    print folder
    articles = os.listdir(unicode(paths.pathCorpus+os.sep+folder))
    for i_article in articles:
        t0 = time()
        article = open(paths.pathCorpus+os.sep+folder+os.sep+i_article+os.sep+"article")
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
        shape = []
        postager = []
        l = 0
        sentences = nltk.tokenize.sent_tokenize(text)
        for sentence in sentences:
            sentence_list = nltk.tokenize.word_tokenize(sentence)
	    if len(sentence_list)>30:
		len_sent.write(folder.encode('utf-8')+': '+sentence.encode('utf-8'))
            #pos_tag_list =  nltk.pos_tag(sentence_list)
            for pos_i, word in enumerate(sentence_list):
                #unknown Anton's kostul'
                if word == '\ufeff':
                    continue
                words.append(word.encode('utf-8'))
                pos = text.find(word, l)
                offset.append(pos)
                l = max(len(word) + pos, l)
		if pos_i<3:
			pos_in_sent.append(pos_i)
		else:
                	pos_in_sent.append(-1)

                stem.append(stemmer.stem(word).encode('utf-8')),
                last_two.append(word[-3:].encode('utf-8')),
                last_three.append(word[-2:].encode('utf-8')),
                isupper.append(word.isupper()),
                istitle.append(word.istitle()),
                isdigit.append(word.isdigit()),
                shape.append(get_shape(word).encode('utf-8')),
                #postager.append(pos_tag_list[pos_i][1])

        dfForArticle.insert(0, 'Word', words)
        dfForArticle.insert(1, 'Offset', offset)
        dfForArticle.insert(2, 'Pos_in_sent', pos_in_sent)
        dfForArticle.insert(3, 'Stem', stem)
        dfForArticle.insert(4, 'LastTwo', last_two)
        dfForArticle.insert(5, 'LastThree', last_three)
        dfForArticle.insert(6, 'IsUpper', isupper)
        dfForArticle.insert(7, 'IsTitle', istitle)
        dfForArticle.insert(8, 'IsDigit', isdigit)
        dfForArticle.insert(9, 'Shape', shape)
        #dfForArticle.insert(10, 'PosTag', postager)

        json_of_article = read_json(paths.pathCorpus+os.sep+folder+os.sep+i_article+os.sep+"res.json")
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

        dfForArticle.insert(2, 'TypeNE', entities_type)

        dfForArticle.to_csv(path_or_buf=paths.pathCorpus+os.sep+folder+os.sep+i_article+os.sep+"features", index_label="id")
        t1 = time()
        print "Finish " + i_article + "time = %f" %(t1-t0)
