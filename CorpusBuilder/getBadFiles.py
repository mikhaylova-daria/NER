import os
import sys
import argparse
from os import listdir
import marking

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default = os.getcwd() + '\\Corpus')
paths = parser.parse_args(sys.argv[1:])

count = 0
errors = open(os.getcwd() + '\\errors.txt', "w")
allfiles = listdir(paths.pathCorpus)
for letter in allfiles:
    articles = listdir(paths.pathCorpus+'\\'+letter)
    print letter
    for name_article in articles:
        patharticle = paths.pathCorpus + '\\'+letter+'\\'+name_article+"\\article"
        pathentites = paths.pathCorpus +'\\'+letter+'\\'+name_article + "\\res.json"
        try:
            json_of_article = marking.read_json(pathentites)
            article = marking.read_article(patharticle)
            first_mistake = len(article)
            for entity in json_of_article:
                if len(entity) == 0:
                    continue
                for pair in entity['Boundaries']:
                    if article[pair[0]:pair[0]+2].lower() != entity['Entity'][0:2]:
                        if first_mistake > pair[0] and pair[0] != 0:
                            first_mistake = pair[0]
            if first_mistake != len(article):
                line = name_article + " " + str(first_mistake) + " " + str(len(article)) + '\n'
                errors.write(line)
                count += 1
        except Exception:
            continue

errors.write("\n\n\n" + str(count))
errors.close()