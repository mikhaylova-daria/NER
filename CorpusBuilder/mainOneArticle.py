#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from nltk import PorterStemmer

#get wiki types

'''
    "C:\\Users\\Toshik\\AML\\Entities.txt" - Типы сущностей, которые мы ищем
    "C:\\Users\\Toshik\\AML\\NewWikiEntities" - Сущности википедии -- Должны называться
        WikiOrganisation, WikiPerson, WikiPopulatedPlace
    "C:\\Users\\Toshik\\AML\\test\\article" - Путь к файлу со статьей
    "C:\\Users\\Toshik\\AML\\test\\links" - Путь к файлу с ссылками в этой статье
    "C:\\Users\\Toshik\\AML\\test\\res.json" -Путь к файлу с ответом
'''

import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--pathEntities', default = os.getcwd() + '\\Entities.txt')
parser.add_argument('--pathWikiEntities', default = os.getcwd() + '\\NewWikiEntities')
parser.add_argument('--pathArticle', default=os.getcwd() + '\\article')
parser.add_argument('--pathLinks', default=os.getcwd() + '\\links')
parser.add_argument('--pathResult', default=os.getcwd() + '\\res.json')
paths = parser.parse_args(sys.argv[1:])

dataTypes = open(paths.pathEntities, 'r')

dataTypesText = dataTypes.read().split('\n')

types = []
for typeStr in dataTypesText:
    type1 = open(paths.pathWikiEntities + "\\Wiki" + typeStr + ".txt", 'r')
    types.append(set(type1.read().decode('utf-8').split('\n')))


f = open(paths.pathLinks, 'r')

wikiPair = f.read().decode('utf-8').split('\n')

answer = []
for typeStr in dataTypesText:
    answer.append([])

allent = set([])
for ent in wikiPair:
    if ent.count('\t') == 0:
        continue
    x = ent[:ent.index('\t')]
    y = ent[ent.index('\t')+1:]
    for i in range(0, len(types)):
        if x.count('http://en.wikipedia.org/wiki/') == 0:
            continue
        if (x[len('http://en.wikipedia.org/wiki/') :] in types[i]) and (y not in allent):
            answer[i].append(y)
            allent.add(y)

#0 - Person, 1 - Organization, 2 - PopulatedPlace

#lemmatizer
data = open(paths.pathArticle, "r")
text1 = data.read().decode('utf-8')

links1 = []
l = 0
for q in text1.split(' '):
    links1.append([l, q])
    l += len(q) + 1

text1 = text1.replace(' - ', ' \u2013 ', text1.count(' - '))
text1 = text1.replace(' -', ' \u2013', text1.count(' -'))
text1 = text1.replace('- ', '\u2013 ', text1.count('- '))
text1 = text1.replace('-', ' - ', text1.count('-'))
text1 = text1.replace('(', '( ', text1.count('('))
text1 = text1.replace(')', ' )', text1.count(')'))
text1 = text1.replace('  ', ' ', text1.count('  ')).split(' ')
text = []
for word in text1:
    text2 = []
    if len(word) == 0:
        continue
    while word[len(word)-1] in [',','.','!','?',':',';']:
        text2.append(word[len(word)-1])
        word = word[:-1]
        if len(word) == 0:
            break
    text.append(word)
    for i in range(len(text2)-1, -1,-1):
        text.append(text2[i])

out = ''

st = PorterStemmer()

def isOk(s):
    if len(s) == 0:
        return False
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
    out += q.lower()
    links.append([l, q])
    l += len(q)

all = dict([])
j = 0
k = 0
fl = 0
for i in range(len(links)):
    if links[i][1][0] == '(':
        k = 1
        continue
    if links[i][1][0] == ')':
        if k == 1:
            j += 1
        k = 0
        continue
    if links[i][1][0] == '-':
        j -= 1
        k = len(links[i-1][1])
        continue
    if links[i][1][0] in [',','.','!','?',':',';']:
        k = 0
        continue
    if j >= len(links1):
        break
    all[links[i][0]] = links1[j][0] + k
    j += 1
    k = 0

#links - lemmatizer 1
#links1 - article 0
#references
text = []
for i in range(len(answer)):
    for word in answer[i]:
        text.append(word)

q = [',', '.', '!', '?', ':', ';']
tmp = []
tx = [text[i] for i in range(len(text)) if len(text[i])>0]
for i in range(len(text)):
    if len(text[i]) == 0:
        continue
    text[i] = text[i].lower()
    text[i] = text[i].replace(' - ', ' \u2013 ', text[i].count(' - '))
    text[i] = text[i].replace(' -', ' \u2013', text1.count(' -'))
    text[i] = text[i].replace('- ', '\u2013 ', text1.count('- '))
    text[i] = text[i].replace('-', ' - ', text[i].count('-'))
    text[i] = text[i].replace(')', ' )', text[i].count(')'))
    text[i] = text[i].replace('(', '( ', text[i].count('('))
    for w in q:
        text[i]=text[i].replace(w, ' '+w, text[i].count(w))
    word = text[i].split(' ')
    s = ''
    for w in word:
        if isOk(w):
            s  += st.stem(w) + ' '
        else:
            s += w + ' '
    tmp.append(s[:-1])

text = tmp

ref = all

article = out

typ = dataTypesText[0]
j = 0
allEntities = []
for ite in range(len(text)):
    word = text[ite]
    if len(word) == 0:
        continue
    i = 0
    if j == len(answer[0]):
        typ = dataTypesText[1]
    if j == len(answer[0]) + len(answer[1]):
        typ = dataTypesText[2]
    j += 1

    k = article.find(' ' + word + ' ')
    bou = []
    while k != -1:
        i = k + len(word)
        if ref.get(k+1) != None:
            bou.append([ref[k + 1],ref[k + 1] + len(tx[ite])])
        k = article.find(' ' + word + ' ', i, len(article))
    if len(bou) > 0:
        allEntities.append([bou, typ, word])

for j in allEntities:
    for k in allEntities:
        if j[2] == k[2]:
            continue
        if j[2].find(k[2]) < 0:
            continue
        x = 0
        y = 0
        while (x < len(j[0]) and y < len(k[0])):
            if k[0][y][0] >= j[0][x][0] and k[0][y][1] <= j[0][x][1]:
                k[0].remove([k[0][y][0],k[0][y][1]])
            if y == len(k[0]) or len(k[0]) == 0:
                break
            if k[0][y][0] > j[0][x][0]:
                x += 1
            else:
                y +=1

outfile = open(paths.pathResult, "w")
outfile.write('[')
for x in allEntities:
    if len(x[0]) > 0:
        json.dump({"Boundaries": x[0], "Type": x[1], "Entity": x[2]}, outfile)
        outfile.write(',')
outfile.write('{}]')
outfile.close()
