__author__ = 'daria'

from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
import nltk.stem.porter

stemmer=nltk.stem.porter.PorterStemmer()



def word2features(sent, i):
    word = sent[i][0].decode('utf-8')
    features = [
        'bias',
        'word.lower=' + stemmer.stem(word),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
    ]

    if i > 0:
        word1 = sent[i-1][0]
        features.extend([
            '-1:word.lower=' + stemmer.stem(word1),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
        ])
    else:
        features.append('BOS')

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        features.extend([
            '+1:word.lower=' + stemmer.stem(word1),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
        ])
    else:
        features.append('EOS')
    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]


tagger = pycrfsuite.Tagger()
tagger.open('fitModel.crfsuite')

input_file = open('features', 'r')
import pandas
import numpy as np
df = pandas.read_csv('features')
test_sents = np.array(df[["Word","TypeNE"]])
X_test = [sent2features(s) for s in test_sents]
y_test = [sent2labels(s) for s in test_sents]


for x in test_sents:
    example_sent = x
    if tagger.tag(sent2features(example_sent))[0]!= sent2labels(example_sent)[0]:
        print x
        print("Predicted:", ' '.join(tagger.tag(sent2features(example_sent))))
        print("Correct:  ", ' '.join(sent2labels(example_sent)))