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


def word2features(sent, i):
    word = sent[0].decode('utf-8')
    features = [
        'bias',
        'word.lower=' + stemmer.stem(word),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
    ]
    '''
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
    '''
    return features


def sent2features(sent):
    return [word2features(sent, 0)]

def sent2labels(sent):
    return [sent[1]]

def sent2tokens(sent):
    return [sent[0]]

input_file = open('features', 'r')

import pandas
import numpy as np
df = pandas.read_csv('features')
train_sents = np.array(df[["Word","TypeNE"]])
print train_sents
#test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))


X_train = [sent2features(s) for s in train_sents]
y_train = [sent2labels(s) for s in train_sents]

#X_test = [sent2features(s) for s in test_sents]
#y_test = [sent2labels(s) for s in test_sents]

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

