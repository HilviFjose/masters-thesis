import pandas as pd 


T_ij = {i: {j: float for j in range(0, 46)} for i in range(0, 46)}


df_distance = pd.read_csv('data/Distances.csv')
dict_distances = df_distance.to_dict(orient='records')


for arc in dict_distances:
    nodes = arc['Unnamed: 0'].replace("'","").replace("(","").replace(")","")
    nodes_list = list(nodes.split(", "))
    T_ij[int(nodes_list[0])][int(nodes_list[1])] = float(arc['0'])





    #days er her entall dager, mens employees er en liste over             

print(T_ij[1][25])
print(T_ij[25][0])