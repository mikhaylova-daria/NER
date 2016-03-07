__author__ = 'daria'

#from sklearn.metrics import classification_report, confusion_matrix
#from sklearn.preprocessing import LabelBinarizer
import os

import pandas
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
        for key in s[1].index:
            features.append(str(key) + '-1=' + '')
    else:
        del next['TypeNE']
        for key in next.index:
            features.append(str(key) + '+1=' + str(next.ix[key]))
    return features


def testFolder(folder):
    print "FOLDER", folder
    letter = folder
    folder = path + os.sep + folder
    tp_f = 0
    tn_f = 0
    fn_f = 0
    fp_f = 0
    articles_list = []
    precision_list = []
    recall_list = []
    F_list = []
    dfTestFolderReport = pandas.DataFrame()
    for article in os.listdir(folder):
        dfTestReport = pandas.DataFrame()
        wordReport = []
        posReport = []
        predictReport = []
        correctReport = []
        df = pandas.read_csv(folder + os.sep + article + os.sep + 'features')

        X_test = []
        y_test = []

        x_sent=[]
        y_sent=[]

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
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        for i, example_sent in enumerate(X_test):
            results = tagger.tag(example_sent)
            for j, result in enumerate(results):
                if result != y_test[i][j]:
                    if result == "No":
                        fn += 1
                    else:
                        fp += 1
                    wordReport.append(df['Word'][pos])
                    posReport.append(pos)
                    predictReport.append(result)
                    correctReport.append(str(y_test[i][j]))
                    #print df['Word'][pos], pos
                    #print "Predicted:", ''.join(result)
                    #print "Correct:  ", ''.join(str(y_test[i][j]))
                else:
                    if result == "No":
                        tn += 1
                    else:
                        tp += 1
                pos += 1
        dfTestReport.insert(0,"Word", wordReport)
        dfTestReport.insert(1, "Position", posReport)
        dfTestReport.insert(2, "Predicted", predictReport)
        dfTestReport.insert(3,"Correct", correctReport)
        dfTestReport.to_csv(folder + os.sep + article + os.sep + "TestReport", index_label=id)
        if tp != 0:
            precision = tp*1./(tp+fp)
            recall = tp*1./(tp+fn)
        else:
            precision = 0
            recall = 0
        if precision + recall != 0:
            F = 2*precision*recall*1./(precision + recall)
        else:
            F = 0
        precision_list.append(precision)
        recall_list.append(recall)
        F_list.append(F)
        articles_list.append(article)
        tp_f += tp
        tn_f += tn
        fn_f += fn
        fp_f += fp
        print article

    dfTestFolderReport.insert(0, "Article", articles_list)
    dfTestFolderReport.insert(1, "Precision", precision_list)
    dfTestFolderReport.insert(2, "Recall", recall_list)
    dfTestFolderReport.insert(3, "F", F_list)
    dfTestFolderReport.to_csv(os.getcwd() + os.sep + "Report" + os.sep + "TestFolderReport" + "_" + letter, index_label=id)
    pr_f = 0
    rc_f = 0
    F_f = 0
    if tp_f != 0:
        pr_f = tp_f*1./(tp_f+fp_f)
        rc_f = tp_f*1./(tp_f+fn_f)
    if pr_f + rc_f != 0:
        F_f = 2*pr_f*rc_f*1./(pr_f + rc_f)
    metrics = [pr_f, rc_f, F_f]
    report[folder] = metrics
    print report
    return

tagger = pycrfsuite.Tagger()
tagger.open('fitModel.crfsuite')
path = "C:\Users\Anton\Documents\Diploma\RandomCorpusTest"

report = dict()
for i in range(65, 91):
    report.setdefault(chr(i))
print report


import multiprocessing
if __name__ == '__main__':
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map(testFolder, os.listdir(path))
