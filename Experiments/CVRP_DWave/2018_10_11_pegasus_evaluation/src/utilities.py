import numpy as np
import pandas as pd
import pdb
import os
import random
import time
import networkx as nx


def generate_input(N=5, save_dir=None):
    outposts = generate_outposts(N)
    max_load = outposts.load.max()
    total_load = outposts.load.sum()
    vehicles = generate_vehicles(max_load, total_load)
    graph_df, graph = generate_graph(outposts)
    
    if save_dir:
        os.makedirs(save_dir)
        outposts.to_csv(os.path.join(save_dir, "outposts.csv"), sep=";")
        vehicles.to_csv(os.path.join(save_dir, "vehicles.csv"), sep=";")
        graph_df.to_csv(os.path.join(save_dir, "graph.csv"), sep=";")

    return outposts, vehicles, graph


def generate_outposts(N):
    outposts = pd.DataFrame(columns=["outpost_id","outpost_name","address","load","latitude","longitude"])
    outposts["outpost_id"] = range(N)
    outposts["load"] = np.random.randint(1, 10, N)
    outposts["latitude"] = (np.random.rand(N) - 0.5) * 10
    outposts["longitude"] = (np.random.rand(N) - 0.5) * 10
    outposts.at[0,"load"] = 0
    outposts.at[0, "latitude"] = 0
    outposts.at[0, "longitude"] = 0

    return outposts


def generate_vehicles(max_load, total_load):
    number_of_vehicles = 1#np.random.randint(1, 4)
    vehicles = pd.DataFrame(columns=["vehicle_id", "capacity"])
    vehicles["vehicle_id"] = range(number_of_vehicles)
    capacity = max_load
    while capacity * number_of_vehicles < total_load:
        capacity += 1

    vehicles["capacity"] = capacity
    return vehicles


def generate_graph(outposts):
    graph_array = [] 
    for i in range(len(outposts)):
        for j in range(len(outposts)):
            if i==j:
                continue
            point_A = (outposts.iloc[i].longitude, outposts.iloc[i].latitude)
            point_B = (outposts.iloc[j].longitude, outposts.iloc[j].latitude)
            distance = distance_between_points(point_A, point_B)
            graph_array.append([i, j, distance])

    graph_df = pd.DataFrame(graph_array, columns=["node_a", "node_b", "cost"])
    graph = read_graph_from_df(graph_df, outposts)
    return graph_df, graph

def read_graph_from_df(graph_df, outposts):
    graph = nx.Graph()

    for _, outpost in outposts.iterrows():
        graph.add_node(outpost.outpost_id, load=outpost.load)

    for _, row in graph_df.iterrows():
        graph.add_edge(row["node_a"], row["node_b"], weight=row["cost"])
    return graph


def distance_between_points(point_A, point_B):
    return np.sqrt((point_A[0] - point_B[0])**2 + (point_A[1] - point_B[1])**2)
