#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import argparse

parser = argparse.ArgumentParser()
#parser.add_argument('--pathArticles', default = os.getcwd() + '/WikiArticles')
parser.add_argument('--pathArticles', default = '/home/daria/corpusArticles')
#parser.add_argument('--pathLinks', default = os.getcwd() + '/WikiLinks')
parser.add_argument('--pathLinks', default='/home/daria/corpusLinks')

#parser.add_argument('--pathCorpus', default = os.getcwd() + '/Corpus')
parser.add_argument('--pathCorpus', default = '/home/daria/Corpus')
paths = parser.parse_args(sys.argv[1:])
if os.path.exists(paths.pathCorpus) == False:
    os.mkdir(paths.pathCorpus)

print paths.pathLinks

if os.path.exists(paths.pathLinks) == False or os.path.exists(paths.pathArticles) == False:
    print "Bad directories!!!"
else:

    os.chdir(paths.pathCorpus)
    import shutil
    from os import listdir
    letters = listdir(paths.pathLinks)
    for letter in letters:
        w = listdir(paths.pathLinks + "/" + letter)
        os.mkdir(letter)
        for ww in w:
            if ww == 'PaxHeader':
                continue
            os.mkdir(paths.pathCorpus.encode('utf-8') + "/" + letter +'/' + ww)
            try:
                shutil.copy2(paths.pathLinks.encode('utf-8') + "/" + letter + '/' + ww, paths.pathCorpus.encode('utf-8') +
                         "/" + letter +'/' + ww+'/links')
                shutil.copy2(paths.pathArticles.encode('utf-8') + "/" + letter + '/' + ww, paths.pathCorpus.encode('utf-8') +
                         "/" + letter +'/' + ww+'/article')
            except Exception:
                continue