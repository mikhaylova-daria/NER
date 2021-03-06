import os
import sys
import argparse
import allFunctions
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathTypes', default = os.getcwd() + '/Entities.txt')
parser.add_argument('--pathWikiEntities', default = os.getcwd() + '/NewWikiEntities')
parser.add_argument('--pathCorpus', default = '/home/daria/Corpus')
paths = parser.parse_args(sys.argv[1:])

wikEntities, types = allFunctions.getWikiEnt(paths.pathTypes, paths.pathWikiEntities)
allfiles = listdir(paths.pathCorpus)


def processing(letter):
    articles = listdir(paths.pathCorpus+'/'+letter)
    print letter
    for name_article in articles:
        pathLinks = paths.pathCorpus +'/'+letter+'/'+name_article + "/links"
        path = paths.pathCorpus +'/'+letter+'/'+name_article + "/article"
        pathout = paths.pathCorpus +'/'+letter+'/'+name_article + "/res.json"
        try:
            allEnt = allFunctions.getNecessaryEnt(pathLinks, types, wikEntities)
            entities = allFunctions.getAllEnt(allEnt)
            lemmaText, lemmaEntities, links, links1, sourceText, sourceEntities = allFunctions.getLemmatizerInfoArt(entities, path)
            mapPairs = allFunctions.getAll(links, links1)
            allEntities = allFunctions.getBoundaries(mapPairs, lemmaEntities, lemmaText, sourceText, sourceEntities, types,
                                                     [len(allEnt[0]),len(allEnt[1]),len(allEnt[2])])
            allEntities = allFunctions.deleteBadEntities(allEntities)
            allFunctions.writeToJSON(pathout, allEntities)
        except Exception:
            continue

import multiprocessing

pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
pool.map(processing, allfiles)
pool.terminate()
