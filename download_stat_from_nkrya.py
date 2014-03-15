import codecs
import urllib2
import urllib
import sys, traceback
import time

def extract_between(text, sub1, sub2, nth=1):
    """
    extract a substring from text between two given substrings
    sub1 (nth occurrence) and sub2 (nth occurrence)
    arguments are case sensitive
    """
    # prevent sub2 from being ignored if it's not there
    if sub2 not in text.split(sub1, nth)[-1]:
        return None
    interm_text = text.split(sub1, nth)[-1].split(sub2, nth)[0]
    interm_text = ''.join(interm_text.split())
    return interm_text

#populate freq dictionary
words = []
freqDictFile  = codecs.open('static/data/ru/freq_hagen_dict.txt', 'a+', encoding='utf-8')
freqLines = freqDictFile.readlines()
freqDictFile.seek(0,2)
for line in freqLines:
    wordEl = line.split('\t')
    words.append(wordEl[0])
print 'Words in freq dictionary: ' + str(len(words))

#populate dictionary
dictFile  = codecs.open('static/data/ru/hagen lemmas only.txt', encoding='utf-8')
lines = dictFile.readlines()

#iterate in dictionary
i = 0
maxIter = 1
for line in lines:
    if i >= maxIter:
        break
    wordEl = line.split('\t')
    word = wordEl[0]
    if word in words:
        continue

    print word

    #form url
    url = 'http://search.ruscorpora.ru/search.xml?env=alpha&mycorp=&mysent=&mysize=&mysentsize=&spd=&text=lexgramm&mode=main&sort=gr_tagging&lang=ru&nodia=1&parent1=0&level1=0&lex1='+urllib.quote(word.encode('utf8'))+'&gramm1=&sem1=&sem-mod1=sem&sem-mod1=sem2&flags1=&m1=&parent2=0&level2=0&min2=1&max2=1&lex2=&gramm2=&sem2=&sem-mod2=sem&sem-mod2=sem2&flags2=&m2='

    #make a query
    try:
        response = urllib2.urlopen(url)
    except:
        print 'Error: no response from the server'
        continue
    time.sleep(0)
    html = response.read()


        # #read webpage from file
        # htmlFile  = codecs.open('test.htm', encoding='windows-1251')
        # html = htmlFile.read()
        # htmlFile.close()

    #parse
    docs_tot = extract_between(html,'<span class="stat-number">','</span>',1)
    words_tot = extract_between(html,'<span class="stat-number">','</span>',3)
    docs = extract_between(html,'<span class="stat-number">','</span>',4)
    occurences = extract_between(html,'<span class="stat-number">','</span>',5)

    #if nothing found
    try:
        if len(docs_tot) > 30:
            docs_tot = 1
            words_tot = 1
            docs = 0
            occurences = 0
    except:
        print 'Error: we are banned.'
        break
        # print docs_tot
        # print words_tot
        # print docs
        # print occurences

    words.append(word)
    freqLine = word + '\t' + str(float(occurences)/float(words_tot)*1000000)\
               + '\t' + str(float(docs)/float(docs_tot))
    freqDictFile.write(freqLine + '\n')
    print freqLine
    i += 1

response.close()
freqDictFile.close()
print 'Done for now'



