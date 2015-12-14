import json
from nltk import PorterStemmer
def deleteBadEntities(Entities):
    allEntities = Entities
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
    return allEntities

def writeToJSON(pathResult, allEntities):
    outfile = open(pathResult, "w")
    outfile.write('[')
    for x in allEntities:
        if len(x[0]) > 0:
            json.dump({"Boundaries": x[0], "Type": x[1], "Entity": x[2]}, outfile)
            outfile.write(',')
    outfile.write('{}]')
    outfile.close()

def findEndOfWord(s,word,position):
    w = position
    k = word.count(' ')
    i = 0
    while i<=k:
        w += 1
        if s[w]in[' ','\n', u'\xa0']:
            i += 1
    w -= 1
    while s[w] in [',', '.', '!', '?', ':', ';', ')', '\u0027']:
        w -= 1

    return w-position+1

def getBoundaries(allRef, ent, lemmaText, sourceText, sourceEntities, types, countOfTypes):
    entities = ent
    ref = allRef
    article = " " + lemmaText + " "
    typ = types[0]
    j = 0
    allEntities = []
    for ite in range(len(entities)):
        word = entities[ite]
        if len(word) == 0:
            continue
        i = 0
        if j == countOfTypes[0]:
            typ = types[1]
        if j == countOfTypes[0] + countOfTypes[1]:
            typ = types[2]
        j += 1

        k = article.find(' ' + word + ' ')
        bou = []
        while k != -1:
            i = k + len(word)
            if ref.get(k) != None:
                bou.append([ref[k],ref[k]+findEndOfWord(sourceText, sourceEntities[ite], ref[k])])
            k = article.find(' ' + word + ' ', i, len(article))
        if len(bou) > 0:
            allEntities.append([bou, typ, word])
    return allEntities

def isOk(s):
    if len(s) == 0:
        return False
    for c in s:
        if ord(c) > 128:
            return False
    return True


def getLemmatizerInfo(entities, pathArticle):

    data = open(pathArticle, "r")
    text1 = data.read().decode('utf-8')

    sourceText = text1

    links1 = []
    l = 0
    for q in text1.split():
        if q == '\ufeff':
            continue
        links1.append([text1.find(q,l), q])
        l = len(q) + 1 + text1.find(q,l)

    text1 = text1.replace(' - ', ' \u2013 ', text1.count(' - '))
    text1 = text1.replace(' -', ' \u2013', text1.count(' -'))
    text1 = text1.replace('- ', '\u2013 ', text1.count('- '))
    text1 = text1.replace('-', ' - ', text1.count('-'))
    text1 = text1.replace('(', '( ', text1.count('('))
    text1 = text1.replace(')', ' )', text1.count(')'))
    text1 = text1.replace(' \u0027', ' \u301E', text1.count(' \u0027'))
    text1 = text1.replace('\u0027', ' \u0027', text1.count('\u0027'))
    text1 = text1.split()
    if text1[0] == u'\ufeff':
        text1=text1[1:]
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

    q = [',', '.', '!', '?', ':', ';']
    tmp = []
    sourceEntities = [entities[i] for i in range(len(entities)) if len(entities[i])>0]

    for i in range(len(entities)):
        if len(entities[i]) == 0:
            continue
        entities[i] = entities[i].lower()
        entities[i] = entities[i].replace(' - ', ' \u2013 ', entities[i].count(' - '))
        entities[i] = entities[i].replace(' -', ' \u2013', entities[i].count(' -'))
        entities[i] = entities[i].replace('- ', '\u2013 ', entities[i].count('- '))
        entities[i] = entities[i].replace('-', ' - ', entities[i].count('-'))
        entities[i] = entities[i].replace(')', ' )', entities[i].count(')'))
        entities[i] = entities[i].replace('(', '( ', entities[i].count('('))
        entities[i] = entities[i].replace('\u0027', ' \u0027', entities.count('\u0027'))
        for w in q:
            entities[i]=entities[i].replace(w, ' '+w, entities[i].count(w))
        word = entities[i].split(' ')
        s = ''
        for w in word:
            if isOk(w):
                s  += st.stem(w) + ' '
            else:
                s += w + ' '
        tmp.append(s[:-1])
    return out, tmp, links, links1, sourceText, sourceEntities

def getAll(links,links1):
    all = dict([])
    j = 0
    k = 0
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
            j-=1
            continue
        if links[i][1][0] in [',','.','!','?',':',';']:
            k = 0
            continue
        if links[i][1][0] == '\u0027':
            continue
        if j >= len(links1):
            break
        all[links[i][0]] = links1[j][0] + k
        j += 1
        k = 0
    return all

def getWikiEnt(pathEntities, pathWikiEntities):
    dataTypes = open(pathEntities, 'r')

    dataTypesText = dataTypes.read().split('\n')

    types = []
    for typeStr in dataTypesText:
        type1 = open(pathWikiEntities + "\\Wiki" + typeStr + ".txt", 'r')
        types.append(set(type1.read().decode('utf-8').split('\n')))

    return types, dataTypesText

def getNecessaryEnt(pathLinks, dataTypesText, types):
    f = open(pathLinks, 'r')

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
            if x.count('/wiki/') == 0:
                continue
            if (x[len('/wiki/'):] in types[i]) and (y not in allent):
                answer[i].append(y)
                allent.add(y)
    return answer

def getAllEnt(ent):
    allEnt = []
    for i in range(len(ent)):
        for word in ent[i]:
            allEnt.append(word)
    return allEnt