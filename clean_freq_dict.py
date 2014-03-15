__author__ = 'Drumsmaster'
import estimator_add
import codecs
import sys

#read dict from file
fileName = 'static/data/ru/freq_hagen_dict.txt'
dic = []
wordList = []
dictFile  = codecs.open(fileName, encoding='utf-8')
for line in dictFile.readlines():
    try:
        word, freq, doc = line.strip().split('\t')
    except:
        print line
    else:
        wordElement = {'word':word,'freq':freq,'doc':doc}
        if word in wordList:
            pass
        else:
            if word[0] == u'*':
                continue
            dic.append(wordElement)
            wordList.append(word)
dictFile.close()

print len(dic)
#sort dict
dic.sort(key=lambda x: (-float(x['freq']),-float(x['doc'])))

#write to file
newFileName = 'static/data/ru/freq_hagen_dict_cleaned.txt'
newDictFile  = codecs.open(newFileName, 'w', encoding='utf-8')
for wordElement in dic:
    line = wordElement['word']+'\t'+wordElement['freq']+'\t'+wordElement['doc']+'\n'
    newDictFile.write(line)
newDictFile.close()

