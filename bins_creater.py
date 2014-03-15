__author__ = 'Drumsmaster'
import estimator

binNum = 40
minBinSize = 300

globalDict = estimator.PopulateDictionary('static/data/ru/freq_hagen_dict_cleaned.txt')
globalDict.sort(key=lambda x: (-float(x['freq']),-float(x['doc'])))
bins = estimator.MakeBinsLinear(globalDict,binNum,minBinSize)

#print bins
i = 1
for bin in bins:
    print str(i)+' '+str(bin['min_rank'])+' '+str(bin['mid_rank'])+' '+str(bin['max_rank'])+' '+str(bin['binsize'])
    i += 1

estimator.SaveBinsToFile(bins,'static/data/ru/coarse_bins.txt')

