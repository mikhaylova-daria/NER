pathCommon = "C:\\Users\\Toshik\\AML\\NewWikiEntities"

pathTypes = "C:\\Users\\Toshik\\AML\\Entities.txt"
dataTypes = open(pathTypes, 'r')

dataTypesText = dataTypes.read().split('\n')

types = []
for typeStr in dataTypesText:
    type1 = open(pathCommon + "\\Wiki" + typeStr + ".txt", 'r')
    types.append(set(type1.read().split('\n')))

f = open("C:\\Users\\Toshik\\AML\\1\\links", 'r')
wikiPair = f.read().split('\n')

answer = []
for typeStr in dataTypesText:
    answer.append(open("C:\\Users\\Toshik\\AML\\" + "\\nevada" + typeStr + ".txt", 'w'))

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
            answer[i].write(y + '\n')
            allent.add(y)
