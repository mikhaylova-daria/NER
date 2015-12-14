#coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
dataset_path = "C:\\Users\\Toshik\\machine_learning\\mipt2015ml\\5_SVM_and_Linear_regression\\linear_train.txt"
dataset_file = open(dataset_path, 'r')
dataset_text = dataset_file.read().split('\n')
data = [line[:line.find(',')] for line in dataset_text]
answer = [line[line.find(',')+2:] for line in dataset_text]
qq = []
for line in answer:
    if len(line) > 0:
        qq.append((int(line)))



dataset_path = "C:\\Users\\Toshik\\machine_learning\\mipt2015ml\\5_SVM_and_Linear_regression\\12321.txt"
dataset_file = open(dataset_path, 'w')
for i in range(len(qq)):
    if qq[i] == 1:
        dataset_text = dataset_file.write(data[i])
        dataset_text = dataset_file.write('\n')

from sklearn.svm import SVC
model = SVC()

dataset_path = "C:\\Users\\Toshik\\machine_learning\\mipt2015ml\\5_SVM_and_Linear_regression\\linear_test.txt"
dataset_file = open(dataset_path, 'r')
dataset = dataset_file.read().split('\n')

import numpy as np
feature = np.array([])

for line in data:
    if line[0].islower():
        feature += 0
    else:
        feature += 1

model.fit(feature, qq)
print model.predict_proba(dataset)