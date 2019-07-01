import numpy as np
import pandas as pd
import os
import networkx as nx
import pdb

def import_all_data(data_path, load_vehicles=True):
    outposts_path = os.path.join(data_path, "outposts.csv")
    vehicles_path = os.path.join(data_path, "vehicles.csv")
    graph_path = os.path.join(data_path, "graph.csv")
    outposts = pd.read_csv(outposts_path, sep=';')
    vehicles = None
    if load_vehicles:
        vehicles = pd.read_csv(vehicles_path, sep=';')
    graph = read_graph_from_file(graph_path, outposts)
    return outposts, vehicles, graph


def read_graph_from_file(graph_path, outposts):
    graph_df = pd.read_csv(graph_path, sep=';')
    graph = read_graph_from_df(graph_df, outposts)
    return graph

def read_graph_from_df(graph_df, outposts):
    graph = nx.Graph()

    for _, outpost in outposts.iterrows():
        graph.add_node(outpost.outpost_id, load=outpost.load)

    for _, row in graph_df.iterrows():
        graph.add_edge(row["node_a"], row["node_b"], weight=row["cost"])
    return graph
