__author__ = 'daria'

from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
import nltk.stem.porter

stemmer=nltk.stem.porter.PorterStemmer()


print(sklearn.__version__)


def word2features(s):

    features = ['bias']
    del s[1]['TypeNE']
    for key in s[1].index:
        features.append(str(key) + '=' + str(s[1].ix[key]))
    return [features]

def word2labels(s):
    return [s[1]['TypeNE']]


input_file = open('features', 'r')

import pandas
import numpy as np
df = pandas.read_csv('features')
del df['Offset']
train_sents = df

#test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))


X_train = [word2features(s) for s in df.iterrows()]
y_train = [word2labels(s) for s in df.iterrows()]


trainer = pycrfsuite.Trainer(verbose=False)

for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)


trainer.set_params({
    'c1': 1.0,   # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 50,  # stop earlier

    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})


#save model as file
trainer.train('fitModel.crfsuite')

