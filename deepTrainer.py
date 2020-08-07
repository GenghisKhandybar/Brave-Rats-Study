from __future__ import absolute_import, division, print_function
import numpy as np
import matplotlib.pyplot as plt
import random as rand
import csv
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from keras.utils import to_categorical
from keras.models import load_model
import time

from agent import agent
import braveRatsGame

def qualityTest(models,trials):#,trainerAI):
    dummies = 0
    for i in range(trials):
        dummies += abs(braveRatsGame.game(0, models)-1) 
    return dummies/trials



def getTwoModels(within, indexUse = -1):
    models = []
    models.append(braveRatsGame.getRandomModel(modelBank, within))
    models.append(braveRatsGame.getRandomModel(modelBank, within))
    if(indexUse != -1):
        models[rand.randint(0,1)] = modelBank[indexUse]
    return models
    
def createDataSet(n): 
    dataSet = [[],[]]
    for i in range(n):
        '''
        if(playerType == 1):
            within = int(len(modelBank)/3)
            print("Play game?")
            ans = input()
            if(ans != "p"):
                break
        '''
        if(i%100 ==0):
            print("Data Progress: " + str(i))
        
        newReport = braveRatsGame.game(["all","all"]) #To use two specific models: getTwoModels(within,indexUse = indexUse)
        predictors = newReport[0]
        targets = newReport[1]

        #dataSetPredictors = np.append(dataSetPredictors,predictors,axis=1)
        #dataSetTargets = np.append(dataSetTargets,targets,axis=1)

        for j in range(len(predictors)):
            #if(len(predictors[j]!=52)):
                #print(len(predictors[j]))
            dataSet[0].append(predictors[j])
            dataSet[1].append(targets[j])
        
    return dataSet

def tensorLearn(dataSet, serialNum): #Next time: make this accept an array of models
    predictors = np.array(dataSet[0])
    targets = np.array(dataSet[1])
    input_shape = (52,)#(len(stateOfGame(["human","human"]).get1dVars(0,0)),)

    print("predictors: " + str(np.shape(predictors)))
    print("targets: " + str(np.shape(targets)))
    print(str(input_shape))

    model = Sequential()
    model.add(Dense(150, activation = 'relu', input_shape= input_shape))
    model.add(Dense(125, activation = 'softmax')) #TODO 11/8/19 changed these from relu to softmax
    model.add(Dense(100, activation = 'softmax'))
    model.add(Dense(2, activation = 'softmax'))
    model.compile(optimizer = 'sgd', loss = 'categorical_crossentropy', metrics = ['accuracy'])

    model.fit(predictors,targets, epochs=5)

    label = 'ratGuru' + str(serialNum) + '.h5'
    model.save(label)
    return model

def diagnoseGameTime(modelBank): #Tests average time of 100 games.
    avgTime = 0
    for i in range(100):
        start = time.time()
        braveRatsGame.game(0,[braveRatsGame.getRandomModel(modelBank),braveRatsGame.getRandomModel(modelBank)])
        end = time.time()
        difference = end - start
        print(difference)
        avgTime += difference/100
    print("Average Time Per Game: " + str(avgTime))

def loadTrainedModels(iterator): #Creates a bank of models from iterator
    #Example : loadTrainedModels(range(0,66))
    modelBank = ["random"]
    for i in iterator:
        print("Loading Model: " + str(i))
        label = 'ratGuru' + str(i) + '.h5'
        modelBank.append(load_model(label))
    return modelBank

def fightSequense(start,end):
    for i in range(start,end):
        print("Loading Model: " + str(i))
        label = 'ratGuru' + str(i) + '.h5'
        model = load_model(label)
        braveRatsGame.game(1,[model,model])

def loadData():
    predictors = []
    targets = []
    with open('ratPredictors.csv', newline = '') as csvfile:
        ratreader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
        for row in ratreader:
            predictors.append(row)
    with open('ratTargets.csv', newline = '') as csvfile:
        ratreader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
        for row in ratreader:
            targets.append(row)
    return [predictors, targets]

def trainLoop(modelBank,fullDataSet, startpoint): #Main loop: Train AI, save every 25th version
    for i in range(startpoint,99999999): #modelsToLoad-1,99999999999):
        print("Starting Training:" + str(i))
        newDataSet = createDataSet(500)
        fullDataSet[0].extend(newDataSet[0])
        fullDataSet[1].extend(newDataSet[1])
        print("FullDataSet Length: " + str(len(fullDataSet[0])))
        
        """ #To use random subsets from full dataset
        dataSet = [[],[]]
        for j in range(50):
            start = rand.randint(0,len(fullDataSet[0])-1)
            end = min(len(fullDataSet[0])-1, start + int(len(fullDataSet[0])/100))
            #print(fullDataSet[0][choose])
            dataSet[0].extend(fullDataSet[0][start:end])
            dataSet[1].extend(fullDataSet[1][start:end])
        """
        if(i%25 == 0):
            """
            newDataSet = createDataSet(modelBank, 99999, playerType = 1)
            for j in range(50): #AI should learn much more from player inputs
                fullDataSet[0].extend(newDataSet[0])
                fullDataSet[1].extend(newDataSet[1])
            """
            with open('ratPredictors.csv', 'w', newline = '') as csvfile:
                ratwriter = csv.writer(csvfile, delimiter = ' ', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
                for l in range(len(fullDataSet[0])):
                    ratwriter.writerow(fullDataSet[0][l])
            with open('ratTargets.csv', 'w', newline = '') as csvfile:
                ratwriter = csv.writer(csvfile, delimiter = ' ', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
                for l in range(len(fullDataSet[0])):
                    ratwriter.writerow(fullDataSet[1][l])
        currentModel = tensorLearn(fullDataSet, i)
        modelBank.append(currentModel)

#modelBank = ["random","random"]
#modelBank = loadTrainedModels(range(174,274))
#trainLoop(modelBank,loadData(),0)