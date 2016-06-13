#!/usr/bin/env python

import argparse
import datetime
import os
import sys

import pycrfsuite

parser = argparse.ArgumentParser()
parser.add_argument('--pathCorpus', default=os.getcwd() + os.sep + 'Corpus')
paths = parser.parse_args(sys.argv[1:])

timeReport = str(datetime.datetime.now())
#pathReport = paths.pathCorpus+"/../Report/"+ timeReport
pathReport = ".."+os.sep+".."+os.sep+"Report" + os.sep + timeReport
os.mkdir(pathReport)

folders = os.listdir(unicode(paths.pathCorpus))

from time import time

def instances():
    feature_names_kostul = False
    feature_names = str()
    for number, folder in enumerate(folders):
        t0 = time()
        print folder
        articles = os.listdir(unicode(paths.pathCorpus+os.sep+folder))
        for article in articles:
            f=open(unicode(paths.pathCorpus+os.sep+folder+os.sep+article+os.sep+'features1'))
            xseq = []
            yseq = []

            previous_line = ""
            current_line = ""
            next_line = ""

            for  i_line, line in enumerate(f):
                if (i_line < 2):
                    current_line = line
                    if feature_names_kostul is False:
                        feature_names = current_line.split('\t')
                        feature_names_kostul = True
                    continue
                current_line = next_line
                next_line = line


                features = current_line.split('\t')
                prev_features = previous_line.split('\t')
                next_features = next_line.split('\t')
                if (len(features) < 4): continue

                if features[0] == 'id':
                    continue
                # if the current word is the first in the sentence then features[4]=='0'
                if features[4] == '0' and len(yseq) != 0:
                    # An empty line presents an end of a sequence.
                    yield xseq, yseq
                    previous_line = str()
                    xseq = []
                    yseq = []
                # Append attributes to the item.
                item = dict()

                if (features[1] == '.'):
                    item = {('Stem', '.')}
                else:
                    v2w_fetures = list()

                    # there are id, name, offset and type information from 0 to 4th pos in csv with features
                    # 5 - pos in sent
                    for i in range(5, 13):
                        #item[feature_names[i]] = (features[i]).decode("utf-8")
                        value = (features[i]).decode("utf-8")
                        v2w_fetures += [(feature_names[i], value)]
                        if len(next_features) > 1:
                            value = (next_features[i]).decode("utf-8")
                            v2w_fetures += [(str(feature_names[i]) + '+1', value)]
                        if len(prev_features) > 1:
                            value = (prev_features[i]).decode("utf-8")
                            v2w_fetures += [(str(feature_names[i]) + '-1', value)]

                    #for i in range(13, len(feature_names)):
                    #    # Weighted attribute
                    #    value = float(features[i])
                    #    if (abs(value) > 1e-10):
                    #        v2w_fetures += [(feature_names[i], str(round(value, 2)))]

                    if v2w_fetures:
                        item.update(dict(v2w_fetures))
                    else:
                        continue

                if len(item)>1:
                    # Append the item to the item sequence.
                    xseq.append(item)
                    # Append the label to the label sequence.
                    yseq.append(features[3])

                previous_line = current_line

            if xseq:
                yield xseq, yseq
            f.close()
        t1 = time()
        print folder + " Time= %f" %(t1-t0)

# Create a Trainer object.
trainer = pycrfsuite.Trainer(verbose=False)

# Read training instances from corpus and set them to trainer.
for xseq, yseq in instances():
    x = pycrfsuite.ItemSequence(xseq)
    trainer.append(x, yseq)
    #print x.items()


# Use L2-regularized SGD and 1st-order dyad features.
trainer.select('l2sgd', 'crf1d')


# Set the coefficient for L2 regularization to 0.1
trainer.set_params({
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 1000,  # stop earlier
    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})
# trainer.set_params({
#     'c1': 1.0,   # coefficient for L1 penalty
#     'c2': 1e-3,  # coefficient for L2 penalty
#     'max_iterations': 1000,  # stop earlier
#
#     # include transitions that are possible, but not observed
#     'feature.possible_transitions': True
# })
# Start training; the training process will invoke trainer.message()
# to report the progress.

t0 = time()
trainer.train(pathReport+"/fitModel"+'.crfsuite')
t1 = time()
print "Time of training:= %f" %(t1-t0)
tagger = pycrfsuite.Tagger()
tagger.open(pathReport+"/fitModel"+'.crfsuite')
tagger.dump(pathReport+ os.sep +'Dump')
