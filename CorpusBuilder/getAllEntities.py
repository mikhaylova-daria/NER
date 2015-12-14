pathCommon = "C:\\Users\\Toshik\\AML\\Entities"

pathTypes = "C:\\Users\\Toshik\\AML\\Entities.txt"
dataTypes = open(pathTypes, 'r')

dataTypesText = dataTypes.read().split('\n')

types = []
newTypes = []

for typeStr in dataTypesText:
    type1 = open(pathCommon + "\\" + typeStr + ".txt", 'r')
    types.append(set(type1.read().split('\n')))
    newTypes.append(open(pathCommon + "\\New" + typeStr + ".txt", 'w'))

def doStr(entity):
    s = ''
    for x in entity:
        s += x
    return x

for i in range(0, len(types)):
    for w in types[i]:
        newTypes[i].write(doStr(w.split('_')) + '\n')
    newTypes[i].close()