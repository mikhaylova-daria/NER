#-*- coding: utf-8 -*-
from __future__ import unicode_literals
from nltk import PorterStemmer
path = "C:\\Users\\Toshik\\AML\\1\\article"
data = open(path, "r")
text1 = data.read().decode('utf-8')

links1 = []
l = 0
for q in text1.split(' '):
    links1.append([l, q])
    l += len(q) + 1


text1 = text1.replace('-', ' - ', text1.count('-'))
text1 = text1.replace('(', '( ', text1.count('('))
text1 = text1.replace(')', ' )', text1.count(')'))
text1 = text1.replace('  ', ' ', text1.count('  ')).split(' ')
text = []
for word in text1:
    text2 = []
    while word[len(word)-1] in [',','.','!','?',':',';']:
        text2.append(word[len(word)-1])
        word = word[:-1]
        if len(word) == 0:
            break
    text.append(word)
    for i in range(len(text2)-1, -1,-1):
        text.append(text2[i])
path1 = "C:\\Users\\Toshik\\AML\\Train\\nevada"
out = open(path1, "w")

st = PorterStemmer()

def isOk(s):
    for c in s:
        if ord(c) > 128:
            return False
    return True

l = 0
links = []
for word in text:
    if isOk(word):
        q = st.stem(word) + ' '
    else:
        q = word + ' '
        q = q.encode('utf-8')
    out.write(q.lower())
    links.append([l, q])
    l += len(q)

out.close()

all = dict([])
j = 0
k = 0

for i in range(len(links)):
    if links[i][1][0] == '('.encode('utf-8'):
        k = 1
        continue
    if links[i][1][0] == '-'.encode('utf-8'):
        j -= 1
        k = len(links[i-1][1])
        continue
    if links[i][1][0] in [','.encode('utf-8'),'.'.encode('utf-8'),'!'.encode('utf-8'),'?'.encode('utf-8'),':'.encode('utf-8'),';'.encode('utf-8')]:
        k = 0
        continue
    if links[i][1][0] == ')'.encode('utf-8'):
        if k == 1:
            j += 1
        k = 0
        continue
    if j>=len(links1):
        break
    all[links[i][0]] = [links1[j][0] + k, len(links1[j][1])]
    j += 1
    k = 0

out1 = open("C:\\Users\\Toshik\\AML\\Train\\refnevada", 'w')
i = 0
for x in all.items():
    out1.write(str(x[0]) + ' ' + str(x[1][0]) + ' ' + str(x[1][1]) + ',')
out1.close()


#links - lemmatizer 1
#links1 - article 0