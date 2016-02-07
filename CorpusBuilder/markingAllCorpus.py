import marking
import os
import sys
import argparse
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default = os.getcwd() + '\\DashaCorpus')
parser.add_argument('--pathHTMLs', default = os.getcwd() + '\\0602NERCorpus')
paths = parser.parse_args(sys.argv[1:])
if os.path.exists(paths.pathHTMLs) == False:
    os.mkdir(paths.pathHTMLs)
allfiles = listdir(paths.pathCorpus)
for q1 in allfiles:
    q2 = listdir(paths.pathCorpus+'\\'+q1)
    print q1
    if os.path.exists(paths.pathHTMLs+"\\"+q1) == False:
        os.mkdir(paths.pathHTMLs+"\\"+q1)
    for q3 in q2:
        path = paths.pathCorpus +'\\'+q1+'\\'+q3 + "\\article"
        pathout = paths.pathCorpus +'\\'+q1+'\\'+q3 + "\\res.json"
        try:
            json_of_article = marking.read_json(pathout)
            article = marking.read_article(path)
            entities = marking.get_entities(json_of_article)
            marking.make_html(article, entities, paths.pathHTMLs+"\\"+q1+"\\"+q3+".html")
        except Exception:
            continue