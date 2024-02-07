import pandas as pd
import numpy as np
import sklearn.metrics
from sklearn.metrics.pairwise import haversine_distances
from datetime import datetime, timedelta


df_employees = pd.read_csv("data/test_data/EmployeesNY.csv")
df_nodes = pd.read_csv("data/test_data/NodesNY.csv")
df_visits = pd.read_csv("data/test_data/VisitsNY.csv")


def travel_matrix(df):
        # Positions
        nodes_lat_lon = list(df_nodes["location"])
        distance_array = np.array(nodes_lat_lon)
        distances = haversine_distances(distance_array, distance_array)
        print("haversine", distances)

        # Distance matrix

        D_ij = haversine(lat_lon, lat_lon) * 6371

        # Travel time matrix
        speed = 20

        T_ij = np.empty(
            shape=(self.num_nodes_and_depots,
                   self.num_nodes_and_depots), dtype=timedelta
        )

        for i in range(self.num_nodes_and_depots):
            for j in range(self.num_nodes_and_depots):
                T_ij[i][j] = (
                    timedelta(hours=(D_ij[i][j] / speed)
                              ).total_seconds()
                )

        # rush hour modelling:
        if not (df.iloc[0]["Requested Pickup Time"].weekday() == 5):
            for k in range(self.n):
                for l in range(self.n):
                    if df.iloc[k]["Requested Pickup Time"].hour >= 15 and df.iloc[k]["Requested Pickup Time"].hour < 17 and df.iloc[l]["Requested Pickup Time"].hour >= 15 and df.iloc[l]["Requested Pickup Time"].hour < 17:
                        T_ij[k][l] = T_ij[k][l]*R_F
                        T_ij[k+self.n][l] = T_ij[k+self.n][l]*R_F
                        T_ij[k][l+self.n] = T_ij[k][l+self.n]*R_F
                        T_ij[k+self.n][l+self.n] = T_ij[k+self.n][l+self.n]*R_F

        return T_ij

T_ij = travel_matrix(df_nodes)
print("Dette er er matrisa:", T_ij)