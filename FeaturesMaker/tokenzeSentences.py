__author__ = 'daria'

from nltk.corpus import gutenberg

import os
import sys
import argparse
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default =  os.getcwd()  + '/Corpus')
paths = parser.parse_args(sys.argv[1:])
