__author__ = 'daria'

import nltk
#from sklearn.metrics import classification_report, confusion_matrix
#from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
import nltk.stem.porter

stemmer=nltk.stem.porter.PorterStemmer()


print(sklearn.__version__)


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



input_file = open('features', 'r')

import pandas

df = pandas.read_csv('features')
del df['Offset']
train_sents = df

#test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))

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

