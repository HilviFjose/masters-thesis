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
        rad_lat = [math.radians(float(i.replace(",", "").split()[0])) for i in df["location"]]
        rad_long = [math.radians(float(i.replace(",", "").split()[1])) for i in df["location"]]
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
        print("T", T_ij)

        # Rush hour modelling:
        for k in range(len(T_ij)):
            average_start_time = df.iloc[k][""]
            if "starting time is between 7 or 9"
            if "starting time is between 15 and 17"
            df.iloc[k]["Requested Pickup Time"].hour >= 15 and df.iloc[k]["Requested Pickup Time"].hour < 17 and df.iloc[l]["Requested Pickup Time"].hour >= 15 and df.iloc[l]["Requested Pickup Time"].hour < 17:
                T_ij[k][l] = T_ij[k][l]*rush_factor
                T_ij[k+self.n][l] = T_ij[k+self.n][l]*rush_factor
                T_ij[k][l+self.n] = T_ij[k][l+self.n]*rush_factor
                T_ij[k+self.n][l+self.n] = T_ij[k+self.n][l+self.n]*rush_factor
               

        return T_ij

matrisa = travel_matrix(df_nodes)
print("Dette er er matrisa:", matrisa)