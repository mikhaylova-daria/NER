import os
import sys
import argparse
import shutil
from os import listdir
import marking
import json
from nltk.corpus import stopwords

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default=os.getcwd() + os.sep + 'Corpus')
parser.add_argument('--pathTrainSet', default=os.getcwd() + os.sep +'RandomizeTrainSet')
paths = parser.parse_args(sys.argv[1:])

number_of_articles = 1000

allfiles = listdir(paths.pathCorpus)

import re
def checkArticle(article, path):
    try:
        if re.search('[*?\|<>/^:]', article) is not None:
            return False
        json_of_article = marking.read_json(path + os.sep + 'res.json')
        filtered_words = [word for word in json_of_article if (len(word) > 0 and
                          word['Entity'] not in stopwords.words('english'))]
        if len(filtered_words) < 7:
            return False
        out_file = open(path + os.sep + 'res.json', "w")
        json.dump(filtered_words, out_file)
        print out_file
        print out_file
        out_file.close()
        return True
    except Exception:
        return False
import random
articles_to_letter = []

if os.path.exists(paths.pathTrainSet) is False:
    os.mkdir(paths.pathTrainSet)

i = 0
while i < number_of_articles:
    letter=random.randint(0, len(allfiles)-1)
    articles_to_letter = listdir(paths.pathCorpus + os.sep + ''+allfiles[letter])
    if len(articles_to_letter) < 7:
        continue
    article_num=random.randint(0,len(articles_to_letter)-1)
    article=articles_to_letter[article_num]
    while checkArticle(article, paths.pathCorpus + os.sep +allfiles[letter] + os.sep + article) is False:
        article_num=random.randint(0, len(articles_to_letter)-1)
        article=articles_to_letter[article_num]
    if os.path.exists(paths.pathTrainSet + os.sep + allfiles[letter]) is False:
        os.mkdir(paths.pathTrainSet + os.sep + allfiles[letter])
    if os.path.exists(paths.pathTrainSet + os.sep + allfiles[letter]  + os.sep+article) is True:
        continue
    shutil.copytree(paths.pathCorpus + os.sep + allfiles[letter] + os.sep +article, paths.pathTrainSet + os.sep +
                    allfiles[letter] + os.sep + article)
    i += 1
