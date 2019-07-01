import numpy as np
import pandas as pd
import pdb
import data_importer
import os
import random
import time
import itertools


def generate_input(N=5, save_dir=None):
    outposts = generate_outposts(N)
    max_load = outposts.load.max()
    total_load = outposts.load.sum()
    vehicles = generate_vehicles(outposts)
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


def generate_vehicles(outposts):
    max_load = outposts.load.max()
    total_load = outposts.load.sum()
    number_of_vehicles = np.random.randint(2, 4)
    vehicles = pd.DataFrame(columns=["vehicle_id", "capacity"])
    vehicles["vehicle_id"] = range(number_of_vehicles)
    number_of_outposts = len(outposts) - 1
    capacity = max_load
    while capacity * number_of_vehicles < total_load:
        capacity += 2
 
    # This checks by brute force if there exists a solution for our problem.
    # e.g. for loads=[6, 5, 5, 1] and vehicles capacities: [9, 9]
    # such an assignment doesn't exist and we need to increase the capacities.
    all_possible_assignments = list(itertools.product(range(number_of_vehicles), repeat=number_of_outposts))
    loads = np.array(outposts.load[1:])
    while True:
        vehicles["capacity"] = capacity
        for assignment in all_possible_assignments:
            correct_counter = 0
            for vehicle_id in range(number_of_vehicles):
                if np.dot(np.array(assignment)==vehicle_id, loads) <= capacity:
                    correct_counter += 1
            # If a single assignment that works exists, return vehicles.
            if correct_counter == number_of_vehicles:
                for vehicle_id in range(number_of_vehicles):
                    print(assignment, loads, np.dot(np.array(assignment)==vehicle_id, loads), capacity)
                return vehicles
        # If no assignment was found - increase vehicles capacity by two.
        capacity += 2
        print("Increased capacity, current value:", capacity)


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
    graph = data_importer.read_graph_from_df(graph_df, outposts)
    return graph_df, graph


def distance_between_points(point_A, point_B):
    return np.sqrt((point_A[0] - point_B[0])**2 + (point_A[1] - point_B[1])**2)

