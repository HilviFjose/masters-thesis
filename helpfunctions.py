

def checkCandidateBetterThanBest(candidateObj, currObj): 
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

# TODO: Tenke på hvordan vi evaluerer om kandidaten er bedre leksikografisk 
def isPromising(candidate_objective, best_objective, local_search_requirement):
    if candidate_objective[0] < best_objective[0]: 
        return False 
    for i in range(1, len(candidate_objective)): 
        if candidate_objective[i] <= best_objective[i] * (1 + local_search_requirement): 
            return True 
    return False