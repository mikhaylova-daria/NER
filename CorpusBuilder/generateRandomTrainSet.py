import os
import sys
import argparse
import  shutil
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathBigCorpus', default = os.getcwd() + '/Corpus')
parser.add_argument('--pathSmallCorpus', default= os.getcwd())

pathBigCorpus = sys.argv[1]
pathSmallCorpus = sys.argv[2]

if os.path.exists(pathSmallCorpus) is False:
    open(pathSmallCorpus, 'w')

random.randint()