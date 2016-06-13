from __future__ import unicode_literals
import os
import sys
import argparse
import allFunctions
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathTypes', default = os.getcwd() + '/Entities.txt')
parser.add_argument('--pathCorpus', default = '/home/daria/Corpus')
paths = parser.parse_args(sys.argv[1:])

allfiles = listdir(paths.pathCorpus)
types = allFunctions.getWikiEnt(paths.pathTypes)


def processing(letter):
    articles = listdir(paths.pathCorpus+'/'+letter)
    print letter
    for name_article in articles:
        pathLinks = paths.pathCorpus +os.sep+letter+os.sep+name_article + os.sep +"person_links"
        path = paths.pathCorpus +os.sep+letter+os.sep+name_article + os.sep+"article"
        pathout = paths.pathCorpus +os.sep+letter+os.sep+name_article + os.sep +"res.json"
        try:
            allEnt = allFunctions.getNecessaryEnt(pathLinks, types)
            entities = allFunctions.getAllEnt(allEnt)
            lemmaText, lemmaEntities, links, links1, sourceText, sourceEntities = allFunctions.getLemmatizerInfoArt(entities, path)
            mapPairs = allFunctions.getAll(links, links1)
            allEntities = allFunctions.getBoundaries(mapPairs, lemmaEntities, lemmaText, sourceText, sourceEntities, types,
                                                     [len(allEnt[0])])
            allEntities = allFunctions.deleteBadEntities(allEntities)
            allFunctions.writeToJSON(pathout, allEntities)
        except Exception:
            print sys.exc_info()
            continue

import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map(processing, allfiles)
    pool.terminate()
