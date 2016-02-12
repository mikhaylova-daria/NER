import marking
import os
import sys
import argparse
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default=os.getcwd() + os.sep + 'Corpus')
parser.add_argument('--pathHTMLs', default=os.getcwd() + os.sep + 'NERCorpus')
paths = parser.parse_args(sys.argv[1:])
if os.path.exists(paths.pathHTMLs) == False:
    os.mkdir(paths.pathHTMLs)
allfiles = listdir(paths.pathCorpus)
for q1 in allfiles:
    q2 = listdir(paths.pathCorpus + os.sep + q1)
    print q1
    if os.path.exists(paths.pathHTMLs + os.sep + q1) == False:
        os.mkdir(paths.pathHTMLs + os.sep + q1)
    for q3 in q2:
        path = paths.pathCorpus + os.sep + q1 + os.sep + q3 + os.sep + "article"
        pathout = paths.pathCorpus + os.sep + q1 + os.sep + q3 + os.sep + "res.json"
        try:
            json_of_article = marking.read_json(pathout)
            article = marking.read_article(path)
            entities = marking.get_entities(json_of_article)
            marking.make_html(article, entities, paths.pathHTMLs + os.sep + q1 + os.sep + q3 + ".html")
        except Exception:
            continue