import multiprocessing
import bz2
import sys
import os
from codecs import open

import ourwikicorpus
import ourutils


def process_article((title, text, number)):
    if re.match(r'\d', title) is not None or re.search(r' list', title) is not None or re.search(r'disambiguation', title) is not None:
        #print title
        return "", []
    text = ourwikicorpus.filter_wiki(text)
    return title.encode('utf8'), ourutils.simple_preprocess(text)


import re


def convert_wiki(infile, processes=multiprocessing.cpu_count()):
    if __name__ == '__main__':
        pool = multiprocessing.Pool(processes)
        texts = ourwikicorpus._extract_pages(bz2.BZ2File(infile))  # generato
        ignore_namespaces = 'Wikipedia Category File Portal Template MediaWiki User Help Book Draft Notes'.split()
        # process the corpus in smaller chunks of docs, because multiprocessing.Pool
        # is dumb and would try to load the entire dump into RAM..
        for group in ourutils.chunkize(texts, chunksize=10 * processes):
            for title, tokens in pool.imap(process_article, group):
                #print title
                if len(tokens) >= 50 and not any(title.startswith(ignore + ':') for ignore in ignore_namespaces):
                    yield title.replace('\t', ' '), tokens
        pool.terminate()


try:
    os.mkdir("pioNER_Wiki_Articles")
except OSError, e:
    if e.errno != 17:
        raise
    pass


numberArticles = int(sys.argv[2])
filledFolder = set()
for title, tokens in convert_wiki(sys.argv[1]):

    dirName = 'different'
    listdir = os.listdir("pioNER_Wiki_Articles/")

    if re.match('\w+', title) is not None:
        dirName = title[0]

    if listdir.count(dirName) == 0:
        os.mkdir("pioNER_Wiki_Articles/" + dirName)

    listdirSize = len(os.listdir("pioNER_Wiki_Articles/" + dirName))

    if listdirSize < numberArticles:
         fileArticle = open("pioNER_Wiki_Articles/" + dirName + "/" + title.replace('/', '_'), "w+", "utf8")
         fileArticle.write(' '.join(tokens))
         fileArticle.close()
    else:
         filledFolder.add(dirName)
         if len(filledFolder) == 27:
             print "ok"
             exit(0)
