#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--pathArticles', default = os.getcwd() + '\\WikiArticles')
parser.add_argument('--pathLinks', default = os.getcwd() + '\\WikiLinks')
parser.add_argument('--pathCorpus', default = os.getcwd() + '\\Corpus')
paths = parser.parse_args(sys.argv[1:])
if os.path.exists(paths.pathCorpus) == False:
    os.mkdir(paths.pathCorpus)

if os.path.exists(paths.pathLinks) == False or os.path.exists(paths.pathArticles) == False:
    print "Bad directories!!!"
else:

    os.chdir(paths.pathCorpus)
    import shutil
    from os import listdir
    x = listdir(paths.pathArticles)
    for q in x:
        os.mkdir(q)
        shutil.copy2(paths.pathLinks + "\\" + q + '.txt', paths.pathCorpus + "\\" + q +'\\'+'\\links')
        shutil.copy2(paths.pathArticles + "\\" + q, paths.pathCorpus + "\\" + q +'\\' + '\\article')