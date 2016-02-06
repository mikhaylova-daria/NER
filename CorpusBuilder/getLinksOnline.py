import multiprocessing

__author__ = 'daria'
import Levenshtein
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

trash = [u'File:', u'Portal:', u'Main_Page', u'Wikipedia:', u'Help:', u'Special:', u'Talk:', u'Category:', u'Template:',
         u'Template_talk:']


# take links with tag "href"
def is_wiki_links(tag):
    if tag.has_attr('href') and tag['href'][:6] == '/wiki/':
        for name in trash:
            if tag['href'].find(name) != -1:
                return False
        return True
    else:
        return False


# estimate links: takes only one links for mention
def mention_estimate(mention, mentions):
    best_href = ''
    if mention != '':
            #print mention
            max = 0.
            for href in mentions[mention]:
                l = Levenshtein.jaro(href[6:], mention)
                if l >= max:
                    max = l
                    best_href = href
    return best_href


import re

# get links using url of article
def get_links_online(url):
    url = url.strip()
    text = requests.get(url).text
    soup = BeautifulSoup(text)
    title = soup.title.text.encode('utf-8')
    dirName = "pioNER_Wiki_Links/different"
    if re.match(r'[A-Z]', url[len("https://en.wikipedia.org/wiki/"):]) is not None:
        dirName = "pioNER_Wiki_Links/" + url[len("https://en.wikipedia.org/wiki/")]
    else:
        return

    links = open(dirName + '/'+url[len("https://en.wikipedia.org/wiki/"):].replace('_', ' '), 'w')
    links.write(url[len("https://en.wikipedia.org/")-1:]+'\t'
                +title[:-len(' - Wikipedia, the free encyclopedia')] + '\n')
    hrefs = defaultdict(set)
    mentions = defaultdict(set)
    wiki_links = soup.find_all(is_wiki_links)
    for tag in wiki_links:
        if tag.has_attr('title'):
            hrefs[tag['href'].encode('utf-8')].add(tag['title'].encode('utf-8'))
        hrefs[tag['href'].encode('utf-8')].add(tag.text.encode('utf-8'))
        mentions[tag.text.encode('utf-8')].add(tag['href'].encode('utf-8'))

    for mention in mentions:
        #links.write(href)
        #for mention in hrefs[href]:
        #if Levenshtein.distance(mention_estimate(mention)[6:], mention)
        # *2./(1+len(mention_estimate(mention)[6:] + mention)) < 0.8:
        if Levenshtein.setratio(mention_estimate(mention, mentions)[6:].split('_'),
                                mention.replace('\xc2\xa0', ' ').split()) >= 0.5:
            #print mention_estimate(mention, mentions), mention
            links.write(mention_estimate(mention, mentions) + '\t'+mention)
            links.write('\n')
    links.close()

import sys
import os


def get_links_online_for_corpus(processes=multiprocessing.cpu_count()):
    if __name__ == '__main__':

        try:
            os.mkdir("pioNER_Wiki_Links")
        except OSError, e:
            if e.errno != 17:
                raise
            pass

        listdir = os.listdir("pioNER_Wiki_Links/")

        dirName = 'different'

        if listdir.count(dirName) == 0:
            os.mkdir("pioNER_Wiki_Links/" + dirName)

        for dirName in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                        'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            if listdir.count(dirName) == 0:
               os.mkdir("pioNER_Wiki_Links/" + dirName)



        if not os.path.exists(sys.argv[1] + 'contents'):
            corpus_contents_file = open("contents", 'w')
            home = sys.argv[1]
            for root, dirs, files in os.walk(home):
                for name in files:
                    corpus_contents_file.write(sys.argv[2] + name.replace(' ', '_')+'\n')
            corpus_contents_file.close()
        pool = multiprocessing.Pool(processes)
        corpus_contents_file = open("contents", 'r')
        pool.map(get_links_online, corpus_contents_file)
        pool.terminate()


get_links_online_for_corpus()




