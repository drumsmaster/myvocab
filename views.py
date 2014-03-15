# -*- coding: utf-8 -*-
from flask import render_template, redirect, render_template_string
from app import app
from forms import FormBase
from wtforms import BooleanField
from flask import request
import urllib
import urlparse
from flask import Flask
from wtforms import SelectMultipleField,widgets
import estimator
import os
from settings import APP_STATIC

#Take a dictionary with words and a list with checked words
#update the dictionary
def UpdateQuestionsDict(words,checkedWords):
    for word in words.keys():
        if word.decode('utf-8') in checkedWords:
            words[word] = 'y'
        else:
            words[word] = 'n'

#Prepare tuples list for wtforms SelectMultipeFields
def MakeNameValueTuples(words):
    i = 0
    tuplesList = []
    for word in words.keys():
        tuplesList.append((word.decode('utf-8'),word.decode('utf-8')))
    return tuplesList        

@app.route('/', methods = ['GET', 'POST'])
@app.route('/step1', methods = ['GET', 'POST'])
def test40():

    userDict = {}
    coarseBinsFileName = os.path.join(APP_STATIC, 'data/ru/coarse_bins.txt')
    coarseBins = estimator.LoadBinsFromFile(coarseBinsFileName)
    estimator.FindReprWords(coarseBins,userDict)
    questions = estimator.MakeDictOfQuestions(coarseBins,userDict)
    questions = estimator.MakeDictUnicode(questions)
    wordsDictList = estimator.SplitDict(questions,4)

    class QuestionsForm(FormBase):
        pass
	
    for i in range(0,4):
        setattr(QuestionsForm,'questions'+str(i),SelectMultipleField(
            'Check words you know',
            choices=MakeNameValueTuples(wordsDictList[i]),
            option_widget=widgets.CheckboxInput(),
            widget=widgets.ListWidget(prefix_label=True)
            ))

    form = QuestionsForm()

    if form.validate_on_submit():
        checkedWords = form.questions0.data + form.questions1.data + form.questions2.data + form.questions3.data
        UpdateQuestionsDict(questions,checkedWords)
        r = urllib.urlencode(questions)
        return redirect('/step2'+'?'+r)
    return render_template('step1.html',form = form)

@app.route('/step2', methods = ['GET', 'POST'])
def step2():

    userDict = {}
    sett = estimator.LoadSettings(os.path.join(APP_STATIC, 'data/ru/settings.txt'))
    minVocWidth = int(sett['minVocWidth'])
    maxVocWidth = int(sett['maxVocWidth'])
    vocWidthCoef = float(sett['vocWidthCoef'])

    for k,v in request.args.items():
        userDict[k] = v
    coarseBinsFileName = os.path.join(APP_STATIC, 'data/ru/coarse_bins.txt')
    coarseBins = estimator.LoadBinsFromFile(coarseBinsFileName)
    estimator.FindReprWords(coarseBins,userDict)
    estimator.UpdateBins(coarseBins,userDict)

    fineBinsFileName = os.path.join(APP_STATIC, 'data/ru/fine_bins.txt')
    fineBins = estimator.LoadBinsFromFile(fineBinsFileName)
    estimator.FindReprWords(fineBins,userDict)

    coarseVocSize = estimator.EstimateVocabSize(coarseBins)
    vocWidth = coarseVocSize*vocWidthCoef
    if vocWidth < minVocWidth:
        vocWidth = minVocWidth
    if vocWidth > maxVocWidth:
        vocWidth = maxVocWidth
    highVocEst = coarseVocSize + vocWidth/2
    lowVocEst = coarseVocSize - vocWidth/2

    mergedBins = estimator.MergeBins(coarseBins,fineBins,lowVocEst,highVocEst)
    estimator.FindReprWords(mergedBins,userDict)
    questions = estimator.MakeDictOfQuestions(mergedBins,userDict)
    questions = estimator.MakeDictUnicode(questions)
    wordsDictList = estimator.SplitDict(questions,4)

    class QuestionsForm(FormBase):
        pass

    for i in range(0,4):
        setattr(QuestionsForm,'questions'+str(i),SelectMultipleField(
            'Check words you know',
            choices=MakeNameValueTuples(wordsDictList[i]),
            option_widget=widgets.CheckboxInput(),
            widget=widgets.ListWidget(prefix_label=True)
            ))

    form = QuestionsForm()

    if form.validate_on_submit():
        checkedWords = form.questions0.data + form.questions1.data + form.questions2.data + form.questions3.data
        UpdateQuestionsDict(questions,checkedWords)

        uniuniQuestions = {}
        for k in questions.keys():
            uniuniQuestions[k.decode('utf-8')] = questions[k].decode('utf-8')

        userDict.update(uniuniQuestions)
        estimator.UpdateBins(mergedBins,userDict)
        fineVocSize = estimator.EstimateVocabSize(mergedBins)
        fineVocSize = estimator.AdaptiveRound(fineVocSize)
        params = {'fineVocSize':unicode(int(fineVocSize))}
        r = urllib.urlencode(params)
        return redirect('/results'+'?'+r)
    return render_template('step2.html',form = form,vocSize=unicode(coarseVocSize))

@app.route('/results')
def results():
    params = {}
    for k,v in request.args.items():
        params[k] = v
    return render_template("results.html",vocSize=params['fineVocSize'])

@app.route('/howitworks')
def howitworks():
    return render_template("howitworks.html")
	
@app.route('/blog')
def blog():
    return render_template("blog.html")