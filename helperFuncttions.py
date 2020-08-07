def oneHotify(possible, value): #Converts an integer to a one-hot array
    toAdd = [0]*possible
    if(value != False):
        toAdd[value] = 1
    return toAdd