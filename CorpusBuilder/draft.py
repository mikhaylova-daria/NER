__author__ = 'daria'



import os


for root, dirs, files in os.walk("/home/daria/NER/CorpusBuilder/WikiLinks/"):
    for name in files:
        f = open("/home/daria/NER/CorpusBuilder/WikiLinks/"+name[0]+'/'+name, 'r')
        for line in f:
            name2=line.split()[0][len('/wiki/'):].replace('_', ' ')
            print name2
            if (name2 != name):
                print "/home/daria/NER/CorpusBuilder/WikiLinks/"+name[0]+'/'+name
                os.rename( "/home/daria/NER/CorpusBuilder/WikiLinks/"+name[0]+'/'+name,
                           name2)
        continue
        f.close()

