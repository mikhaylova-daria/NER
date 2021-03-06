__author__ = 'daria'

import nltk
#from sklearn.metrics import classification_report, confusion_matrix
#from sklearn.preprocessing import LabelBinarizer
import pycrfsuite
import nltk.stem.porter
import pandas

stemmer=nltk.stem.porter.PorterStemmer()

def word2features(prev, s, next):

    features = ['bias']
    del s[1]['TypeNE']
    for key in s[1].index:
        features.append(str(key) + '=' + str(s[1].ix[key]))
    if prev is None:
        for key in s[1].index:
            features.append(str(key) + '-1=' + '')
    else:
        del prev['TypeNE']
        for key in s[1].index:
            features.append(str(key) + '=' + str(prev.ix[key]))
    if next is None:
        for key in s[1].index:
            features.append(str(key) + '-1=' + '')
    else:
        del next['TypeNE']
        for key in next.index:
            features.append(str(key) + '+1=' + str(next.ix[key]))
    return features


#test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))
import os
import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default=os.getcwd() + os.sep + 'Corpus')
paths = parser.parse_args(sys.argv[1:])

trainer = pycrfsuite.Trainer(verbose=False)
folders = os.listdir(unicode(paths.pathCorpus))

from time import time

for folder in folders:
    articles = os.listdir(unicode(paths.pathCorpus+os.sep+folder))
    t0=time()
    for article in articles:
        f=open(unicode(paths.pathCorpus+os.sep+folder+os.sep+article+os.sep+'features'))
        df = pandas.read_csv(f)
        del df['Offset']
        train_sents = df

        X_train = []
        y_train = []

        x_sent=[]
        y_sent=[]
        prev = pandas.DataFrame()
        next = pandas.DataFrame()
        for i, s in enumerate(df.iterrows()):
            if s[1]['Pos_in_sent'] == 0:
                prev = None
            else:
                prev = df.loc[i-1]
            if i < df.shape[0] - 1 and df['Pos_in_sent'][i+1] == 0 or i == df.shape[0]-1:
                next = None
            else:
                next = df.loc[i+1]
            y_sent.append(s[1]['TypeNE'])
            x_sent.append(word2features(prev, s, next))
            if i < df.shape[0] - 1 and df['Pos_in_sent'][i+1] == 0 or i == df.shape[0]-1:
                X_train.append(x_sent)
                y_train.append(y_sent)
                x_sent = []
                y_sent = []

        for xseq, yseq in zip(X_train, y_train):
            trainer.append(xseq, yseq)

    t1=time()
    print folder  + " Time= %f" %(t1-t0)

trainer.set_params({
    'c1': 1.0,   # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 50,  # stop earlier

    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})


#save model as file
trainer.train('fitModel.crfsuite')

