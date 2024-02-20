

def checkCandidateBetterThanCurren(candidateObj, currObj): 
    if candidateObj[0] > currObj[0]: 
        return True 
    if candidateObj[0] < currObj[0]: 
        return False 
    for i in range(1, len(candidateObj)): 
        if candidateObj[i] < currObj[i]: 
            return True 
        if candidateObj[i] > currObj[i]: 
            return False 
    return False