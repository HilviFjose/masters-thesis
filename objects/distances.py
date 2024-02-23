import pandas as pd 
import os
import sys
import math
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders

df_distance = pd.read_csv('data/Distances.csv')

'''
dict_distances = df_distance.to_dict(orient='records')

T_ij = {i: {j: float for j in range(0, df_distance.shape[0])} for i in range(0, 46)}
T_ij = { {} }


for arc in dict_distances:
    nodes = arc['Unnamed: 0'].replace("'","").replace("(","").replace(")","")
    nodes_list = list(nodes.split(", "))
    T_ij[int(nodes_list[0])][int(nodes_list[1])] = float(arc['0'])

'''
T_ij = {}

# Populate the nested dictionary
for index, row in df_distance.iterrows():
    # Extract i, j from the pair in 'Unnamed: 0' column
    i, j = eval(row['Unnamed: 0'])
    
    # Check if i is already a key in the dictionary
    if i not in T_ij:
        T_ij[i] = {}
    
    # Assign the distance to the nested dictionary
    T_ij[i][j] = row['0']



    #days er her entall dager, mens employees er en liste over             

print("0 - 74", math.ceil(T_ij[0][74]))
print("74 - 44", math.ceil(T_ij[74][44]))
print(" 44 - 4", math.ceil(T_ij[44][4]))
print("4 - 0", math.ceil(T_ij[4][0]))
print("sum", str(math.ceil(T_ij[0][74])+math.ceil(T_ij[74][44])+ math.ceil(T_ij[44][4])+math.ceil(T_ij[4][0])))

print("0 - 44", math.ceil(T_ij[0][44]))
print("44 - 74", math.ceil(T_ij[44][74]))
print(" 74 - 4", math.ceil(T_ij[74][4]))
print("4 - 0", math.ceil(T_ij[4][0]))
print("sum", str(math.ceil(T_ij[0][44])+math.ceil(T_ij[44][74])+ math.ceil(T_ij[74][4])+math.ceil(T_ij[4][0])))

print("0 - 74", math.ceil(T_ij[0][74]))
print("74 - 4", math.ceil(T_ij[74][4]))
print(" 4 - 44", math.ceil(T_ij[4][44]))
print("44 - 0", math.ceil(T_ij[44][0]))
print("sum", str(math.ceil(T_ij[0][74])+math.ceil(T_ij[74][4])+ math.ceil(T_ij[4][44])+math.ceil(T_ij[44][0])))

