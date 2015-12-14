import allFunctions
import os
import sys
import argparse
from timeit import default_timer as timer
start = timer()

parser = argparse.ArgumentParser()
parser.add_argument('--pathEntities', default = os.getcwd() + '\\Entities.txt')
parser.add_argument('--pathWikiEntities', default = os.getcwd() + '\\NewWikiEntities')
parser.add_argument('--pathArticle', default=os.getcwd() + '\\article')
parser.add_argument('--pathLinks', default=os.getcwd() + '\\links')
parser.add_argument('--pathResult', default=os.getcwd() + '\\res.json')
paths = parser.parse_args(sys.argv[1:])

wikEntities, types = allFunctions.getWikiEnt(paths.pathEntities, paths.pathWikiEntities)
allEnt = allFunctions.getNecessaryEnt(paths.pathLinks, types, wikEntities)
entities = allFunctions.getAllEnt(allEnt)
lemmaText, lemmaEntities, links, links1, sourceText, sourceEntities = allFunctions.getLemmatizerInfo(entities, paths.pathArticle)
mapPairs = allFunctions.getAll(links, links1)
allEntities = allFunctions.getBoundaries(mapPairs, lemmaEntities, lemmaText, sourceText, sourceEntities, types, [len(allEnt[0]),len(allEnt[1]),len(allEnt[2])])
allEntities = allFunctions.deleteBadEntities(allEntities)
allFunctions.writeToJSON(paths.pathResult, allEntities)

end = timer()

print "Processing time =", end-start