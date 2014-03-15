__author__ = 'Drumsmaster'
import estimator
import math

#returns how close estimation is to the real voc size (in %)
def EstQuality(realNum,estNum):
    return math.fabs(realNum-estNum)/realNum*100

# settings = LoadSettings('data/ru/settings.txt')

#settings
wordstockThresh = 40000
wordstockWidth = 10000
minVocWidth = 20000
maxVocWidth = 40000
vocWidthCoef = 0.4
coarseBinNum = 40
minBinSize = 10
fineBinNum = 400

#prepare - load global dictionary and make fake user dictionary
globalDict = estimator.PopulateDictionary('static/data/ru/freq_hagen_dict_cleaned.txt')
#globalDict.sort(key=lambda x: (-float(x['freq']),-float(x['doc'])))
fakeUserDict = estimator.MakeFakeDict(globalDict,wordstockThresh,wordstockWidth)
print 'Words in fake user dictionary: ' +\
      str(estimator.UserDictSize(fakeUserDict))

#load coarse bins from file
coarseBins = estimator.MakeBinsLinear(globalDict,coarseBinNum,minBinSize)
print 'Number of coarse bins: ' + str(len(coarseBins))

#start with empty user dict
userDict = {}

#assign representative words
estimator.FindReprWords(coarseBins,userDict)

#make first (coarse) list of questions
coarseQuestDict = estimator.MakeDictOfQuestions(coarseBins,userDict)

#get answers and update userDict and bins
estimator.SimulateUserResponse(coarseQuestDict,fakeUserDict)
userDict.update(coarseQuestDict)
estimator.UpdateBins(coarseBins,userDict)

#coarse vocabulary size estimation
coarseVocSize = estimator.EstimateVocabSize(coarseBins)
lowVocEst = estimator.EstimateLowVocLimit(coarseBins,coarseVocSize,0.005)
highVocEst = estimator.EstimateHighVocLimit(coarseBins,coarseVocSize,0.005)
print 'Estimated vocabulary size (coarse): ' + \
      str(lowVocEst) + ' - ' +\
      str(coarseVocSize) +' - ' +\
      str(highVocEst) + ', (' + str(EstQuality(estimator.UserDictSize(fakeUserDict),coarseVocSize)) + '%)'

#load fine bins from file
fineBins = estimator.MakeBinsLinear(globalDict,fineBinNum,minBinSize)
print 'Number of fine bins: ' + str(len(fineBins))

#merge bins
vocWidth = coarseVocSize*vocWidthCoef
if vocWidth < minVocWidth:
    vocWidth = minVocWidth
if vocWidth > maxVocWidth:
    vocWidth = maxVocWidth
highVocEst = coarseVocSize + vocWidth/2
lowVocEst = coarseVocSize - vocWidth/2

print 'Merging in region: ' + str(lowVocEst) + ' - ' + str(highVocEst)
mergedBins = estimator.MergeBins(coarseBins,fineBins,lowVocEst,highVocEst)
print 'Number of merged bins: ' + str(len(mergedBins))

#assign representative words, but make sure that if a word is known
#(based on userdict) - it will be assigned
estimator.FindReprWords(mergedBins,userDict)

#make second (fine) list of questions
fineQuestDict = estimator.MakeDictOfQuestions(mergedBins,userDict)

#get answers and update userDict and bins
estimator.SimulateUserResponse(fineQuestDict,fakeUserDict)
userDict.update(fineQuestDict)
estimator.UpdateBins(fineBins,userDict)

#fine vocabulary size estimation
fineVocSize = estimator.EstimateVocabSize(fineBins)
fineVocSize = estimator.AdaptiveRound(fineVocSize)

#print some statistics
print 'Estimated vocabulary size (fine): ' + str(fineVocSize) +\
      ', (' + str(EstQuality(estimator.UserDictSize(fakeUserDict),fineVocSize)) + '%)'
