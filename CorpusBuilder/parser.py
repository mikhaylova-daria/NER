import multiprocessing
import bz2
import sys, os
from codecs import open

import ourwikicorpus
import ourutils
def process_article((title, text, number)):
    text = ourwikicorpus.filter_wiki(text)
    return title.encode('utf8'), ourutils.simple_preprocess(text)


import re
#multiprocessing.cpu_count()
def convert_wiki(infile, processes=1):
    if __name__ == '__main__':
        pool = multiprocessing.Pool(processes)
        texts = ourwikicorpus._extract_pages(bz2.BZ2File(infile)) # generato
        ignore_namespaces = 'Wikipedia Category File Portal Template MediaWiki User Help Book Draft Notes'.split()
        # process the corpus in smaller chunks of docs, because multiprocessing.Pool
        # is dumb and would try to load the entire dump into RAM..
        for group in ourutils.chunkize(texts, chunksize=10 * processes):
            print 1
            for title, tokens in pool.imap(process_article, group):
                print 2
                if len(tokens) >= 50 and not any(title.startswith(ignore + ':') for ignore in ignore_namespaces):
                    yield title.replace('\t', ' '), tokens
                print 3
        pool.terminate()

i = 0



try:
    os.mkdir("pioNER_Wiki_Articles")
except OSError, e:
    if e.errno != 17:
        raise

    pass
import sys




for title, tokens in convert_wiki(sys.argv[1]):
    dirName = 'different'
    listdir = os.listdir("pioNER_Wiki_Articles/")
    if ( re.match(('\w+'), title) != None ):
        dirName = title[0]
    if (listdir.count(dirName) == 0):
        os.mkdir("pioNER_Wiki_Articles/" + dirName)
    #if (len(os.listdir("pioNER_Wiki_Articles/" + dirName)) == 50):
        #continue
    file = open("pioNER_Wiki_Articles/" + dirName + "/" +title.replace('/', '_'), "w+", "utf8")
    file.write(' '.join(tokens))
    file.close()
    i = i + 1
print "ok"