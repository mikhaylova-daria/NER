#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json

def read_json(path_to_json):
    if os.path.exists(path_to_json) == False:
        return []
    with open(path_to_json) as json_file:
        json_of_article = json.load(json_file)
    return json_of_article

from os import listdir
path = os.getcwd()+'\\Corpus'
f = open("stat.txt", 'w')
x = listdir(path)
for q in x:
    w = listdir(path + "\\" + q)
    for ww in w:
        json_of_article = read_json(path + "\\" + q + "\\" + ww + "\\res.json")
        f.write((ww + " " + str(len(json_of_article)) + "\n").encode('utf-8'))

f.close()