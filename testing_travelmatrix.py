import pandas as pd
import numpy as np
import math
import sklearn.metrics
from sklearn.metrics.pairwise import haversine_distances
from datetime import datetime, timedelta


df_employees = pd.read_csv("data/test_data/EmployeesNY.csv")
df_nodes = pd.read_csv("data/test_data/NodesNY.csv")
df_visits = pd.read_csv("data/test_data/VisitsNY.csv")


def travel_matrix(df):
        # Radians distance matrix
        rad_lat = [math.radians(float(i.replace(",", "").replace("(", "").replace(")", "").split()[0])) for i in df["location"]]
        rad_long = [math.radians(float(i.replace(",", "").replace("(", "").replace(")", "").split()[1])) for i in df["location"]]
        rad_location =list(zip(rad_lat ,rad_long))
        D_ij = haversine_distances(rad_location, rad_location) * 6371
        
        # TODO: De to under her bør inn i config etterhvert
        # Buses in Oslo om average drive in 25 kms/h.
        speed = 40
        rush_factor = 2

        # Travel time matrix - 2D-list with time given in minutes. 
        T_ij = [[0 for _ in range(len(D_ij))] for _ in range(len(D_ij))]
        for i in range(len(D_ij)):
            for j in range(len(D_ij)):
                T_ij[i][j] = (timedelta(hours=(D_ij[i][j] / speed)).total_seconds() / 60)
    
        # Rush hour modelling:
        #TODO: Se på om vi må gjøre dette annerledes og generere rush hour factor basert på tiden som faktisk settes i heuristikken
        for k in range(len(T_ij)):
            average_start_time = (df.iloc[k]["earliestStartTime"] + df.iloc[k]["latestStartTime"]) / 2
            print("averagestarttime", average_start_time)
            # If start time is between 07 and 09. 
            if (df.iloc[k]["earliestStartTime"] >= 420 and df.iloc[k]["earliestStartTime"] <= 540) or (df.iloc[k]["latestStartTime"] >= 420 and df.iloc[k]["latestStartTime"] <= 540):
                for l in range(len(T_ij)):
                    print("old", T_ij[k][l], "new", T_ij[k][l]*rush_factor)
                    T_ij[k][l] = T_ij[k][l]*rush_factor
            # If start time is between 15 and 17.
            if (df.iloc[k]["earliestStartTime"] >= 900 and df.iloc[k]["earliestStartTime"] <= 1020) or (df.iloc[k]["latestStartTime"] >= 900 and df.iloc[k]["latestStartTime"] <= 1020):
                for l in range(len(T_ij)):
                    T_ij[k][l] = T_ij[k][l]*rush_factor
        return T_ij

matrisa = travel_matrix(df_nodes)
print("Dette er er matrisa:", matrisa)