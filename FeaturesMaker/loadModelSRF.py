__author__ = 'daria'

from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
import nltk.stem.porter

def word2features(s):

    features = ['bias']
    del s[1]['TypeNE']
    for key in s[1].index:
        features.append(str(key) + '=' + str(s[1].ix[key]))
    return [features]

def word2labels(s):
    return [s[1]['TypeNE']]

tagger = pycrfsuite.Tagger()
tagger.open('fitModel.crfsuite')

input_file = open('features', 'r')
import pandas
import numpy as np
df = pandas.read_csv('features')
test_sents = df[["Word","TypeNE"]]

X_test = [word2features(s) for s in df.iterrows()]
y_test = [word2labels(s) for s in df.iterrows()]


for i, x in enumerate(X_test):
    example_sent = x
    result = tagger.tag(x)[0]
    #if result != y_test[i][0]:
    if result != 'No':
        print df['Word'][i]
        print "Predicted:", ''.join(result)
        print "Correct:  ", ''.join(str(y_test[i][0]))