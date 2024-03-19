import pandas as pd
import numpy as np
import math
import sklearn.metrics
from sklearn.metrics.pairwise import haversine_distances
from datetime import datetime, timedelta

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from config import main_config


def process_location(x):
    # Hvis x er en streng, fjern parenteser og splitt
    if isinstance(x, str):
        lat_str, lon_str = x.strip("()").split(",")
    # Hvis x er en tuple, bare bruk verdien direkte
    elif isinstance(x, tuple):
        lat_str, lon_str = x
    else:
        raise ValueError("Ukjent datatype i 'location'-kolonnen")
    
    # Konverter strengene til flyttall
    lat = float(lat_str)
    lon = float(lon_str)
    return lat, lon

def travel_matrix(df):
        # Radians distance matrix
        df['lat'], df['lon'] = zip(*df['location'].apply(process_location))

        # Konverterer lat og lon til radianer
        df['rad_lat'] = df['lat'].apply(math.radians)
        df['rad_lon'] = df['lon'].apply(math.radians)

        # Lager en liste av tupler med radianverdier for bredde- og lengdegrad
        rad_location = list(zip(df['rad_lat'], df['rad_lon']))

        # Distance matrix
        D_ij = haversine_distances(rad_location, rad_location) * 6371
        
        # Buses in Oslo om average drive in 25 kms/h.
        speed = main_config.speed
        rush_factor = main_config.rush_factor

        # Travel time matrix - 2D-list with time given in minutes. 
        T_ij = [[0 for _ in range(len(D_ij))] for _ in range(len(D_ij))]
        for i in range(len(D_ij)):
            for j in range(len(D_ij)):
                T_ij[i][j] = (timedelta(hours=(D_ij[i][j] / speed)).total_seconds() / 60)
    
        # Rush hour modelling:
        #TODO: Se på om vi må gjøre dette annerledes og generere rush hour factor basert på tiden som faktisk settes i heuristikken
        for k in range(len(T_ij)):
            average_start_time = (df.iloc[k]["earliestStartTime"] + df.iloc[k]["latestStartTime"]) / 2
            # If start time is between 07 and 09. 
            if (df.iloc[k]["earliestStartTime"] >= 420 and df.iloc[k]["earliestStartTime"] <= 540) or (df.iloc[k]["latestStartTime"] >= 420 and df.iloc[k]["latestStartTime"] <= 540):
                for l in range(len(T_ij)):
                    T_ij[k][l] = T_ij[k][l]*rush_factor
            # If start time is between 15 and 17.
            if (df.iloc[k]["earliestStartTime"] >= 900 and df.iloc[k]["earliestStartTime"] <= 1020) or (df.iloc[k]["latestStartTime"] >= 900 and df.iloc[k]["latestStartTime"] <= 1020):
                for l in range(len(T_ij)):
                    T_ij[k][l] = T_ij[k][l]*rush_factor
        return T_ij


def travel_matrix_without_rush(df):
        # Radians distance matrix
        df['lat'], df['lon'] = zip(*df['location'].apply(process_location))

        # Konverterer lat og lon til radianer
        df['rad_lat'] = df['lat'].apply(math.radians)
        df['rad_lon'] = df['lon'].apply(math.radians)

        # Lager en liste av tupler med radianverdier for bredde- og lengdegrad
        rad_location = list(zip(df['rad_lat'], df['rad_lon']))

        # Distance matrix
        D_ij = haversine_distances(rad_location, rad_location) * 6371
        
        # Buses in Oslo om average drive in 25 kms/h.
        speed = main_config.speed
        rush_factor = main_config.rush_factor

        # Travel time matrix - 2D-list with time given in minutes. 
        T_ij = [[0 for _ in range(len(D_ij))] for _ in range(len(D_ij))]
        for i in range(len(D_ij)):
            for j in range(len(D_ij)):
                T_ij[i][j] = (timedelta(hours=(D_ij[i][j] / speed)).total_seconds() / 60)
    
        return T_ij


#df_nodes = pd.read_csv('data/activities.csv')
#matrisa = travel_matrix(df_nodes)
#print("Dette er er matrisa:", matrisa)