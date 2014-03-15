# -*- coding: utf-8 -*-
import codecs
import random
import math

binTempl = {'min_rank':0,'max_rank':0,'mid_rank':0,'binsize':0,'words':[],'reprWord':u'','isReprWordKnown':'no data'}

def PopulateDictionary(dictionaryFileName):
    dic = []
    dictionaryFile  = codecs.open(dictionaryFileName, encoding='utf-8')
    for line in dictionaryFile.readlines()[2:]:
        line = line.strip()
        word, freq, doc = line.split('\t')
        wordElement = {'word':word,'freq':freq,'doc':doc}
        dic.append(wordElement)
    return dic

#Load bins from file. File has the following structure (separated by \t)):
#minrank,midrank,maxrank,binsize,wordsline
#wordsline contains words. separated by comma
def LoadBinsFromFile(binFileName):
    bins = []
    binFile  = codecs.open(binFileName, encoding='utf-8')
    for line in binFile.readlines()[1:]:
        line = line.strip()
        min_rank,mid_rank,max_rank,binsize,wordsline = line.split('\t')
        words = wordsline.split(',')
        bin = binTempl.copy()
        bin['min_rank'] = int(min_rank)
        bin['max_rank'] = int(max_rank)
        bin['mid_rank'] = int(mid_rank)
        bin['binsize'] = int(binsize)
        bin['words'] = words
        bins.append(bin)
    binFile.close()
    return bins

#Assign a representative word for each bin from its wordlist. If there is a word from userdict in this list,
#make this word the representative
def FindReprWords(bins,userdict):
    for bin in bins:
        for word in bin['words']:
            if word in userdict:
                bin['reprWord'] = word
                break
        if bin['reprWord'] == '':
            bin['reprWord'] = random.choice(bin['words'])

#Make a dictionary with questions from representative words from bins.
#Exclude words from userdict, since it's already known whether they are known are not
def MakeDictOfQuestions(bins,userdic):
    questionsDict = {}
    for bin in bins:
        if not (bin['reprWord'] in userdic):
            questionsDict[bin['reprWord']] = ''
    return questionsDict

def SimulateUserResponse(responseDict,fakeUserDict):
    for word in responseDict.iterkeys():
        if word in fakeUserDict:
            if fakeUserDict[word] == 'y':
                responseDict[word] = 'y'
                continue
        responseDict[word] = 'n'

#assign 'isReprWordKnown' a status from userDIct for each bin
def UpdateBins(bins,userDict):
    for bin in bins:
        if bin['reprWord'] in userDict:
            bin['isReprWordKnown'] = userDict[bin['reprWord']]

def EstimateLowVocLimit(bins,estVocSize,ratioUnknowntoKnown):
    unknownThreshold = estVocSize*ratioUnknowntoKnown
    unknown = 0
    for bin in bins:
        if bin['isReprWordKnown'] == 'n':
            unknown += bin['binsize']
            if unknown > unknownThreshold:
                return bin['min_rank']
    return -1

def EstimateHighVocLimit(bins,estVocSize,ratioKnowntoKnown):
    knownThreshold = estVocSize*ratioKnowntoKnown
    known = 0
    for bin in reversed(bins):
        if bin['isReprWordKnown'] == 'y':
            known += bin['binsize']
            if known > knownThreshold:
                return bin['max_rank']
    return -1

#Bins are sorted from high freq to low freq
def EstimateVocabSize(bins):
    unknownWordsLtoR = []
    knownWordsRtoL = []
    unknownTotal = 0
    for bin in bins:
        if bin['isReprWordKnown'] == 'n':
            unknownTotal += bin['binsize']
        unknownWordsLtoR.append(unknownTotal)

    knownTotal = 0
    for bin in reversed(bins):
        if bin['isReprWordKnown'] == 'y':
            knownTotal += bin['binsize']
        knownWordsRtoL.append(knownTotal)
    knownWordsRtoL.reverse()

    dif = []
    for i in range(0,len(bins)):
        dif.append(int(math.fabs(knownWordsRtoL[i]-unknownWordsLtoR[i])))

    minIndex = dif.index(min(dif))

    return bins[minIndex]['mid_rank']

def AdaptiveRound(vocSize):
    if vocSize < 2000:
        return math.floor(vocSize/50)*50
    else:
        return math.floor(vocSize/100)*100

def MakeBins(dic,binSize):
    #binSize = len(dic)/binNum + 1
    bins = []
    curRank = 0
    while curRank < len(dic):
        lastRank = curRank + binSize - 1
        if len(dic) < lastRank:
            lastRank = len(dic) - 1
        curBin = dict(binTempl)
        wordList = []
        for wordEl in dic[curRank:lastRank+1]:
            wordList.append(wordEl['word'])
        curBin['words'] = wordList
        curBin['min_rank'] = curRank
        curBin['max_rank'] = lastRank
        curBin['mid_rank'] = (curRank + lastRank)/2
        curBin['binsize'] = lastRank - curRank + 1
        bins.append(curBin)
        curRank = lastRank + 1
    return bins

def FreqFunc(f):
    return math.log10(f)

#dic should be sorted from highest freq to lowest
def MakeBinsLogFreq(dic,num):
    bins = []
    highestFreqLog = FreqFunc(float(dic[0]['freq']))
    lowestFreqLog = FreqFunc(float(dic[-1]['freq']))
    freqLogStep = (highestFreqLog - lowestFreqLog)/num
    curRank = 0
    for i in range (1,num+1,1):
        bin = dict(binTempl)
        flexFreqLogStep = freqLogStep
        curHighFreqLog = highestFreqLog - (i-1)*flexFreqLogStep
        curLowFreqLog = curHighFreqLog - flexFreqLogStep
        minRank = curRank
        for r in range(curRank,len(dic)):
            maxRank = r
            if  curLowFreqLog < FreqFunc(float(dic[r]['freq'])) <= curHighFreqLog:
                bin['words'].append(dic[r]['word'])
            else:
                break
        bin['min_rank'] = minRank
        bin['max_rank'] = maxRank
        bin['mid_rank'] = (minRank + maxRank)/2
        bin['binsize'] = maxRank - minRank + 1
        curRank = maxRank + 1
        bins.append(bin)
    return bins

def BinFunc(num,i,total):
    #constant
    #return total/num

    #linear
    a = 900
    binSizeMin = total/num-a*num/2
    return binSizeMin+i*a

#dic should be sorted from highest freq to lowest
def MakeBinsArb(dic,num,binSizeMin,binSizeMax):
    bins = []
    curRank = 0
    for i in range(0,num):
        binSize = BinFunc(num,i,len(dic))
        lastRank = curRank + binSize - 1
        if len(dic) < lastRank:
            lastRank = len(dic) - 1
        if i == num-1:
            lastRank = len(dic) - 1
        curBin = dict(binTempl)
        wordList = []
        for wordEl in dic[curRank:lastRank+1]:
            wordList.append(wordEl['word'])
        curBin['words'] = wordList
        curBin['min_rank'] = curRank
        curBin['max_rank'] = lastRank
        curBin['mid_rank'] = (curRank + lastRank)/2
        curBin['binsize'] = lastRank - curRank + 1
        bins.append(curBin)
        curRank = lastRank + 1
    return bins

#dic should be sorted from highest freq to lowest
def MakeBinsLinear(dic,num,binSizeMin):
    bins = []
    a = (len(dic)/float(num)-binSizeMin)*2/(float(num)-1.0)
    curRank = 0
    for i in range(0,num):
        binSize = binSizeMin+a*i
        lastRank = curRank + binSize
        if i == num-1:
            lastRank = len(dic) - 1
        curBin = dict(binTempl)
        wordList = []
        for wordEl in dic[int(curRank):int(lastRank+1)]:
            wordList.append(wordEl['word'])
        curBin['words'] = wordList
        curBin['min_rank'] = int(curRank)
        curBin['max_rank'] = int(lastRank)
        curBin['mid_rank'] = int((curRank + lastRank)/2)
        curBin['binsize'] = int(lastRank-curRank)
        bins.append(curBin)
        curRank = lastRank + 1.0
    return bins

def UserDictSize(userDict):
    i = 0
    for word in userDict.values():
        if word == 'y':
            i += 1
    return i

def MakeFakeDict(globalDict,tresh,width):

    #probability of knowing a word
    def gauss(x,mean,widthFWHM):
        width = widthFWHM/2.35482
        if x < mean:
            return 1
        return math.exp(-pow(x-mean,2)/(2*pow(width,2)))

    userDict = {}
    i = 1
    for wordElement in globalDict:
        r = random.random()
        ver = gauss(i, tresh, width)
        if  ver >= r:
            userDict[wordElement['word']] = 'y'
        else:
            userDict[wordElement['word']] = 'n'
        i += 1
    return userDict

#merge coarse bins with fine ones. All bins should be sorted high freq to low freq
def MergeBins(coarseBins,fineBins,startRank,endRank):
    mergedBins = []
    for bin in coarseBins:
        if bin['max_rank'] <= startRank:
            mergedBins.append(bin)
    if len(mergedBins)>0:
        startRank = mergedBins[-1]['max_rank']+1
    for bin in fineBins:
        if (bin['min_rank'] >= startRank) and (bin['max_rank'] <= endRank):
            mergedBins.append(bin)
    endRank = mergedBins[-1]['max_rank']+1
    for bin in coarseBins:
        if bin['min_rank'] >= endRank:
            mergedBins.append(bin)
    return mergedBins

def LoadSettings(fileName):
    settings = {}
    settingsFile  = codecs.open(fileName, encoding='utf-8')
    for line in settingsFile.readlines():
        key,value = line.split()
        settings[key] = value
    settingsFile.close()
    return settings

def SaveBinsToFile(bins,fileName):
    binFile  = codecs.open(fileName, 'w', encoding='utf-8')
    binFile.write('min_rank\tmid_rank\tmax_rank\tbinsize\twordsline\n')
    for bin in bins:
        wordsline = random.choice(bin['words'])
        binLine = str(bin['min_rank'])+'\t'\
                  +str(bin['mid_rank'])+'\t'\
                  +str(bin['max_rank'])+'\t'\
                  +str(bin['binsize'])+'\t'\
                  +wordsline+'\n'
        binFile.write(binLine)
    binFile.close()

def SplitDict(inputDict,n):
    size = len(inputDict.keys())/float(n)
    dictList = []
    for i in range(0,n):
        dictList.append(dict(inputDict.items()[int(i*size):int((i+1)*size)]))
    return dictList

def MergeDicts(dictList):
    mergedDict = {}
    for d in dictList:
        mergedDict.update(d)
    return mergedDict

def MakeDictUnicode(dict):
    uniDict = {}
    for k, v in dict.iteritems():
        uniDict[unicode(k).encode('utf-8')] = unicode(v).encode('utf-8')
    return uniDict

# # settings = LoadSettings('data/ru/settings.txt')
#
# #settings
# wordstockThresh = 30000
# wordstockWidth = 30000
# minVocWidth = 10000
# maxVocWidth = 20000
# coarseBinSize = 1000
# fineBinSize = 100
#
# #prepare - load global dictionary and make fake user dictionary
# globalDict = estimator_add.PopulateDictionary('data/ru/freq_voc_no_dupl.txt')
# globalDict.sort(key=lambda x: (-float(x['freq']),-float(x['d'])))
# fakeUserDict = MakeFakeDict(globalDict,wordstockThresh,wordstockWidth)
# # print 'Words in fake user dictionary: ' +\
# #       str(estimator.UserDictSize(fakeUserDict))
#
# #load coarse bins from file
# #coarseBins = MakeBins(globalDict,coarseBinSize)
# coarseBins = LoadBinsFromFile('data/ru/coarse_bins.txt')
# print 'Number of coarse bins: ' + str(len(coarseBins))
# #SaveBinsToFile(coarseBins,'data/ru/coarse_bins.txt')
#
# #start with empty user dict
# userDict = {}
#
# #assign representative words
# FindReprWords(coarseBins,userDict)
#
# #make first (coarse) list of questions
# coarseQuestDict = MakeDictOfQuestions(coarseBins,userDict)
#
# #get answers and update userDict and bins
# SimulateUserResponse(coarseQuestDict,fakeUserDict)
# userDict.update(coarseQuestDict)
# UpdateBins(coarseBins,userDict)
#
# #coarse vocabulary size estimation
# coarseVocSize = EstimateVocabSize(coarseBins)
# lowVocEst = EstimateLowVocLimit(coarseBins,coarseVocSize,0.005)
# highVocEst = EstimateHighVocLimit(coarseBins,coarseVocSize,0.005)
# print 'Estimated vocabulary size (coarse): ' + \
#       str(lowVocEst) + ' - ' +\
#       str(coarseVocSize) +' - ' +\
#       str(highVocEst) + ', (' + str(estimator.EstQuality(estimator.UserDictSize(fakeUserDict),coarseVocSize)) + '%)'
#
# #load fine bins from file
# fineBins = MakeBins(globalDict,fineBinSize)
# print 'Number of fine bins: ' + str(len(fineBins))
#
# #merge bins
# #mergedBins = MergeBins(coarseBins,fineBins,coarseVocSize-vocWidth/2,coarseVocSize+vocWidth/2)
# if (highVocEst-lowVocEst) < minVocWidth:
#     highVocEst = coarseVocSize + minVocWidth/2
#     lowVocEst = coarseVocSize - minVocWidth/2
#
# if (highVocEst-lowVocEst) > maxVocWidth:
#     highVocEst = coarseVocSize + maxVocWidth/2
#     lowVocEst = coarseVocSize - maxVocWidth/2
#
# print 'Merging in region: ' + str(lowVocEst) + ' - ' + str(highVocEst)
# mergedBins = MergeBins(coarseBins,fineBins,lowVocEst,highVocEst)
# print 'Number of merged bins: ' + str(len(mergedBins))
#
# #assign representative words, but make sure that if a word is known
# #(based on userdict) - it will be assigned
# FindReprWords(mergedBins,userDict)
#
# #make second (fine) list of questions
# fineQuestDict = MakeDictOfQuestions(mergedBins,userDict)
#
# #get answers and update userDict and bins
# SimulateUserResponse(fineQuestDict,fakeUserDict)
# userDict.update(fineQuestDict)
# UpdateBins(fineBins,userDict)
#
# #fine vocabulary size estimation
# fineVocSize = EstimateVocabSize(mergedBins)
#
# #print some statistics
# # for bin in mergedBins:
# #     print bin['min_rank'],bin['max_rank'],bin['binsize'],bin['isReprWordKnown']
# print 'Estimated vocabulary size (fine): ' + str(fineVocSize) +\
#       ', (' + str(estimator.EstQuality(estimator.UserDictSize(fakeUserDict),fineVocSize)) + '%)'
#
# # total = 0
# # for bin in mergedBins:
# #     total += int(bin['binsize'])
# #     print bin['min_rank'],bin['mid_rank'],bin['max_rank'],bin['binsize'],bin['isReprWordKnown']

