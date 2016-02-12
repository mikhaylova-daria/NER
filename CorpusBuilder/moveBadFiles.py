import os
import sys
import argparse
import  shutil
from os import listdir

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default = os.getcwd() + '/Corpus')
parser.add_argument('--pathErrors', default= os.getcwd())
parser.add_argument('--pathBadArticles', default= os.getcwd() + '/BadArticles')
paths = parser.parse_args(sys.argv[1:])

allfiles = listdir(paths.pathCorpus)
def processing(letter):
    try:
        f = open(paths.pathErrors+'/'+letter+'_errors.txt')
        errors = f.read().split('\n')
        if os.path.exists(paths.pathBadArticles+'/'+letter) is False:
            os.mkdir(paths.pathBadArticles+'/'+letter)
        print letter
        for bad_article in errors:
            if bad_article.count(' ') < 2:
                continue
            name_bad_article = bad_article[:bad_article.rfind(' ', 0, bad_article.rfind(' ') - 1)]
            if os.path.exists(paths.pathCorpus+'/'+letter+'/'+name_bad_article) is True:
                shutil.move(paths.pathCorpus+'/'+letter+'/'+name_bad_article, paths.pathBadArticles+'/'+letter+'/'+name_bad_article)
    except Exception as e:
        print "Ooooops", letter, sys.exc_info()



import multiprocessing
if __name__ == '__main__':
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map(processing, allfiles)
    pool.terminate()