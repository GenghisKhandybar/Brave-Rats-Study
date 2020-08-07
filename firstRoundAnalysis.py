import numpy as np
import matplotlib.pyplot as plt
import imageio
import sys
import copy

import deepTrainer
#from deepTrainer import loadTrainedModels


#Use of spy = 0.5 victory except against 6
#Princess v Prince = 4 victories


def getBasicWinValues():
    #"Modified conventional" value grid
    #Opponent play:  0    1    2    3    4    5    6    7
    winValues = np.array([
                [   0,   0,-0.5,   0,   0,  -1,   0,   0],
                [   0,   0,-1.5,   1,  -2,  -1,  -1,   4],
                [ 0.5, 1.5,   0, 1.5,-1.5,  -1,  -1,-0.5],
                [   0,  -1,-1.5,   0,   1,  -1,   1,  -1],
                [   0,   2, 1.5,  -1,   0,  -1,  -1,  -1],
                [   1,   1,   1,   1,   1,   0,  -1,  -1],
                [   0,   1,   1,  -1,   1,   1,   0,  -1],
                [   0,  -4, 0.5,   1,   1,   1,   1,   0]
                ])
    return winValues

usable = np.array([[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]) #First = What you have left, Second = What opponent has left

interVals = np.zeros(8)

avgInterVals = np.zeros(8)

generations = 500; #chose this

imageNames = []

#indir = sys.argv[1]

figN = 0
(general, spy) = ((0,0),(0,0))




def symetricalDeepen(winValues):
    global interVals

    largest = -100
    largestIndex = -1
    for i in range(8):
        if(usable[0][i] == 1):
            current = np.sum(vals[i])
            if(current > largest):
                largestIndex = i
                largest = current
    interVals[largestIndex] += 1 
    for i in range(8):
        for j in range(8):
            vals[i,j] = winValues[i,j]*interVals[j]
    
def plotCards(interVals, name = ""): #bar graph
    global figN
    global imageNames
    plt.clf()
    plt.title(name + str(figN))
    p1 = plt.bar(range(8),interVals)
    for i in range(8):
        plt.text(i - 0.18, interVals[i]+0.001 , round(interVals[i],2))
    imageNames.append(name + str(figN))
    plt.savefig(name + str(figN))
    figN+=1

def checkWinValues(winValues): #Checks that the winvalues grid is fair, prints any unfair locations
    for i in range(8):
        for j in range(8):
            if(abs(winValues[i][j]) != abs(winValues[j][i])):
                print(str(i) + str(j))

def symetricalTest():
    global avgInterVals
    global generations
    global imageNames
    global indir
    for i in range(generations):
        symetricalDeepen()
        avgInterVals += interVals
        makePlot()
        plotCards(interVals, name = "Generation ")
        print("Generation " + str(i) + " " + str(interVals))
    """
    images = []
    #for i in range(generations):
        images.append(imageio.imread(indir + "/" + imageNames[i]))
    imageio.mimsave('gifVersion', images,'GIF')
    avgInterVals = avgInterVals / sum(avgInterVals)
    plotCards(avgInterVals,"Average best at generation ")
    """

def neuralValuation(gameState, modelBank): #Creates a grid of win probabilities for each way the current gamestate could change this turn.
    winValues = np.zeros((8,8))
    for i in range(8):
        for j in range(8):
            if(gameState.cardsAvailiable[0][i] ==1 and gameState.cardsAvailiable[1][j]==1):
                testState = copy.deepcopy(gameState)
                testState.selected[0] = i
                testState.selected[1] = j
                testState.advanceGameState()
                for model in modelBank:
                    pass #predict win chance

modelBank = deepTrainer.loadTrainedModels(range(250,274))
neuralValuation(deepTrainer.stateOfGame(["random","random"]), modelBank)
