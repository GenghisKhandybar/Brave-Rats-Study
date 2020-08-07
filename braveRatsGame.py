import numpy as np
from helperFunctions import oneHotify
import random as rand

class stateOfGame:
    cardsAvailiable =[[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]
    generalsUsed = [0,0]
    spyUsed = [0,0]
    victories = [0,0]
    holds = [0,0]
    card = 0 #how many rounds have passed
    players = ["all","all"]
    selected = [False,False] #Chosen Cards
    def __init__(self,players):
        self.cardsAvailiable =[[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]
        self.selected = [False,False] #Chosen Cards
        self.generalsUsed = [0,0]
        self.spyUsed = [0,0]
        self.victories = [0,0]
        self.holds = [0,0]
        self.card = 0 #how many rounds have passed
        self.players = ["all","all"]
        self.players = players

    def getCards(self,player):
        return self.cardsAvailiable[player]
        
    def getVictories(self,player):
        return self.victories[player]
    
    def gameNotDone(self):
        return (self.victories[0]<4 and self.victories[1] <4 and self.card <8)

    def get1dVars(self,player,cardChoice): #Gets variables to make prediction or record data from for a player perspective
        players = [player, abs(player-1)]
        state = np.empty(0)
        for i in players:
            state = np.append(state,self.cardsAvailiable[i]) #Last
            state = np.append(state,self.generalsUsed[i])
            state = np.append(state,self.spyUsed[i])
            state = np.append(state,oneHotify(4,min(self.victories[i],3))) #Adds total victories for p1
            state = np.append(state,oneHotify(4,min(self.holds[i],3))) #Adds total holds for p1
        if(self.spyUsed[player]==True):
            state = np.append(state,oneHotify(8,self.selected[players[1]]))
        else:
            state = np.append(state,[0]*8)
        state = np.append(state,oneHotify(8,cardChoice))
        return state

    def advanceGameState(self): #replacement for nextRoundGameState
        values = ((self.selected[0]+self.generalsUsed[0]*2), (self.selected[1]+self.generalsUsed[1]*2)) #Card Values 
        effects = (self.selected[0], self.selected[1])
        if(effects[0] == 5 or effects[1] == 5): #WIZARD
            effects = (8, 8) #irrelevant numbers
        if(values[0] < values[1]): #For the inner function, v0 > v1
            a = -innerMatchup([values[1],values[0]],[effects[1],effects[0]])
        else:
            a = innerMatchup(values,effects)
            
        for i in range(2):
            if(effects[i] == 4): #Ambassador : Gives you +1 hold
                self.holds[i] += 1 

        if(a>0):
            self.victories[0] += a + self.holds[0]
            self.resetHolds()
        elif(a<0):
            self.victories[1] += -a + self.holds[1]
            self.resetHolds()
        else:
            self.holds[0] += 1
            self.holds[1] += 1

        self.spyUsed = [0,0]
        self.generalsUsed = [0,0]
        for i in range(2):
            if(effects[i] == 6):
                self.generalsUsed[i] = 1
            if(effects[i] == 2 and effects[abs(i-1)] != 2):
                self.spyUsed[i] = 1
            self.cardsAvailiable[i][self.selected[i]] = 0
        self.selected=[False,False]
        self.card+=1

    def resetHolds(self):
        self.holds = [0,0]

def game(playerTypes,simpleReturn=False): #Plays one game of brave rats
    #detailed return makes function return a whole log of each turn
    gameState = stateOfGame(playerTypes)
    fullGameReport = []
    winnerReport = []
    
    while(gameState.gameNotDone()):
        isSpy = 0 #Spy system could probably be reformed
        for i in range(2): #if there's a spy, conduct asymetrical round
            if(gameState.spyUsed[abs(i-1)] == 1): #If your opponent used a spy, choose your card
                isSpy = 1
                gameState.selected[i] = select(gameState, i)
                gameState.selected[abs(i-1)] = select(gameState, abs(i-1))
        if(isSpy == 0): #If there was no spy, conduct normal round
            for i in range(2):
                gameState.selected[i] = select(gameState, i)
        fullGameReport.append(gameState.get1dVars(0,gameState.selected[0]))
        fullGameReport.append(gameState.get1dVars(1,gameState.selected[1]))

        gameState.advanceGameState()

    #Game is over
    winner = 0 
    if(gameState.victories[1] > gameState.victories[0]):
        winner = 1 #Winner = 1 if p1 won

    if(gameState.victories[1] == gameState.victories[0]):
        winner = rand.randint(0,1)
    loser = abs(winner-1)
    for i in range(len(fullGameReport)):
        if(i%2==0): #[0,1] = loss from player perspective, [1,0] = win from player pespective
            winnerReport.append((np.array([loser,winner])))
        else:
            winnerReport.append((np.array([winner,loser]))) #Alternates perspectives between p0 and p1
    if(simpleReturn):
        return(winner)
    else:
        #print(np.shape(fullGameReport))
        return([fullGameReport, winnerReport])

def select(gameState, player, modelOverride = False, printThoughts=False): #Get selection based off 1 AI
    opponent = abs(player-1)
    model = gameState.players[player]
    if(modelOverride!=False):
        model = modelOverride
    if(model=="human"):
        itemList = " 0  1  2  3  4  5  6  7"
        print("Selecting card for player " + str(player))
        print("Your hand:")
        print(itemList)
        print(str(gameState.cardsAvailiable[player]))
        print("Opponent's hand:")
        print(itemList)
        print(str(gameState.cardsAvailiable[opponent]))
        print("Choose a card.")
        if(gameState.spyUsed[player] == 1):
            print("Opponent's choice (by spy): " + str(gameState.selected[opponent]))
        valid = 0
        while(valid==0):
            try:
                ans = int(input())
                if(ans == 8): #Press 8 to get neural selection
                    return select(gameState,player,modelOverride="all")
                valid = gameState.cardsAvailiable[player][ans]
            except:
                print("You've already used that card. Your hand: " + str(gameState.cardsAvailiable[player]))           
        return(ans)
    elif(model == "random"):
        while(True):
            tryThis = rand.randint(0,7)
            if(gameState.cardsAvailiable[player][tryThis] == 1):
                return tryThis
    elif(model == "all"):
        return select(gameState,player,modelOverride = getRandomModel())
    #Now, use neural net to get answer
    qualityList = [] #How good each is predicted to be -not currently used
    bestQuality = -1
    bestIndex = -1
    predictList = [gameState.get1dVars(player,0)] #np.array([gameState.get1dVars(player,0)])
    for i in range(1,8):
        predictList = np.append(predictList, [gameState.get1dVars(player,i)],axis=0)
    predictions = model.predict(predictList)
    for i in range(8):
        quality = predictions[i][0]
        qualityList.append(quality)
        if(quality>bestQuality and gameState.cardsAvailiable[player][i] == 1):
            bestQuality = quality
            bestIndex = i
    if(printThoughts == 1):
        print(qualityList)
    return bestIndex

def innerMatchup(values,effects): #This is used for matchup to compare cards
    if(values[0] == values[1] or effects[0] == 0 or effects[1] == 0):
        return 0
    if(effects[0] == 7):
        if(effects[1] == 1):
            return -4
        else:
            return 1
    if(effects[0] == 3 or effects[1] == 3):
        values = (values[1],values[0])
    if(values[0] > values[1]):
        return (1)
    else:
        return (-1)

def getRandomModel(modelBank, within = -1): #Selects a model either randomly or semi-randomly
    if(within == -1):
        index = rand.randint(0,len(modelBank)-1)
    elif(within ==0):
        index = -1
    else:
        index = rand.randint(len(modelBank)-1-within,len(modelBank)-1)
    if(index == 0):
        #print("Using Rat Guru RANDOM")
        return "random"
    #print("Using Rat Guru " + str(index))
    return modelBank[index]