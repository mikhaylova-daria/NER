__author__ = 'daria'

#from sklearn.metrics import classification_report, confusion_matrix
#from sklearn.preprocessing import LabelBinarizer
import pycrfsuite


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
        for key in prev.index:
            features.append(str(key) + '-1=' + '')
    else:
        del next['TypeNE']
        for key in next.index:
            features.append(str(key) + '+1=' + str(next.ix[key]))
    return features



tagger = pycrfsuite.Tagger()
tagger.open('fitModel.crfsuite')

input_file = open('features', 'r')
import pandas

df = pandas.read_csv('features')
test_sents = df[["Word","TypeNE"]]
X_test = []
y_test = []

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
        X_test.append(x_sent)
        y_test.append(y_sent)
        x_sent = []
        y_sent = []



pos = 0
for i, example_sent in enumerate(X_test):
    results = tagger.tag(example_sent)
    for j, result in enumerate(results):
        if result != 'No':
            print df['Word'][pos], pos
            print "Predicted:", ''.join(result)
            print "Correct:  ", ''.join(str(y_test[i][j]))
        pos += 1