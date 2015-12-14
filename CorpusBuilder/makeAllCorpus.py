import os
import sys
import argparse
import allFunctions
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathTypes', default = os.getcwd() + '\\Entities.txt')
parser.add_argument('--pathWikiEntities', default = os.getcwd() + '\\NewWikiEntities')
parser.add_argument('--pathCorpus', default = os.getcwd() + '\\TCorpus')
paths = parser.parse_args(sys.argv[1:])

wikEntities, types = allFunctions.getWikiEnt(paths.pathTypes, paths.pathWikiEntities)
allfiles = listdir(paths.pathCorpus)
for q1 in allfiles:
    q2 = listdir(paths.pathCorpus+'\\'+q1)
    print q1
    for q3 in q2:
        pathLinks = paths.pathCorpus +'\\'+q1+'\\'+q3 + "\\links"
        path = paths.pathCorpus +'\\'+q1+'\\'+q3 + "\\article"
        pathout = paths.pathCorpus +'\\'+q1+'\\'+q3 + "\\res.json"
        allEnt = allFunctions.getNecessaryEnt(pathLinks, types, wikEntities)
        entities = allFunctions.getAllEnt(allEnt)
        lemmaText, lemmaEntities, links, links1, sourceText, sourceEntities = allFunctions.getLemmatizerInfo(entities, path)
        mapPairs = allFunctions.getAll(links, links1)
        allEntities = allFunctions.getBoundaries(mapPairs, lemmaEntities, lemmaText, sourceText, sourceEntities, types, [len(allEnt[0]),len(allEnt[1]),len(allEnt[2])])
        allEntities = allFunctions.deleteBadEntities(allEntities)
        allFunctions.writeToJSON(pathout, allEntities)