import codecs

types = ['s','a','num','anum','v','adv','spro','apro','advpro','pr','conj',
         'part','intj']

def PopulateDictionary(dictionaryFileName):
    dic = []
    dictionaryFile  = codecs.open(dictionaryFileName, encoding='utf-8')
    for line in dictionaryFile.readlines()[1:]:
        line = line.strip()
        word, poS, freq, r, d, doc = line.split('\t')
        wordElement = {'word':word,'PoS':poS,'freq':freq,'r':r,'d':d,'doc':doc}
        dic.append(wordElement)
    return dic
	
def histogram(dic,binSize):
    binStatTemplate = {'min rank':0,'max rank':0,'avg rank':0,'avg freq':0.,
                   's':0,'a':0,'num':0,'anum':0,'v':0,'adv':0,'spro':0,
                   'apro':0,'advpro':0,'pr':0,'conj':0,'part':0,'intj':0,
                   'elements total':0}
    binStat = []
    bins = []
    curRank = 0
    while curRank < len(dic):
        lastRank = curRank + binSize - 1
        if len(dic) < lastRank:
            lastRank = len(dic) - 1
        curBin = dic[curRank:lastRank+1]
        #do stat
        curBinStat = dict(binStatTemplate)
        curBinStat['min rank'] = curRank
        curBinStat['max rank'] = lastRank
        curBinStat['avg rank'] = (curRank + lastRank)/2
        freq = 0
        for wordElement in curBin:
            freq += float(wordElement['freq'])
            curBinStat[wordElement['PoS']] += 1
        freq = freq / (lastRank - curRank + 1)
        curBinStat['avg freq'] = freq
        curBinStat['elements total'] = lastRank - curRank + 1
        #modify all lists
        bins.append(curBin)
        binStat.append(curBinStat)
        curRank = lastRank + 1
    return bins,binStat
