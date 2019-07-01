from minorminer import find_embedding
import dwave_networkx as dnx
from problem import Problem
import utilities
import numpy as np
import pandas as pd
import pdb


def main():

    all_chimera_results = []
    all_pegasus_results = []

    for graph_size in range(4, 16):
        print("TSP size:", graph_size)
        outposts, vehicles, graph = utilities.generate_input(graph_size)
        starting_point = 0 
        vehicles_partitions = []
        current_partition = [graph_size - 1]
        use_capacity_constraints = False
        qubo_params = {'cost_constant': 10, 'constraint_constant': 400, 'capacity_constraint_constant': 200}

        problem = Problem(vehicles=vehicles,
                          outposts=outposts,
                          vehicles_partition=current_partition,
                          graph=graph,
                          starting_point=starting_point,
                          use_capacity_constraints=use_capacity_constraints)
        n = 10
        # Since no embeddings above this size can be found for dnx.chimera_graph(16, 16, 4),
        # it can be omitted to speed up calculations.
        if graph_size > 11:
            chimera_results = [[np.nan, np.nan, np.nan] for i in range(n)]
        else:
            chimera_results = evaluate_embedding(problem, qubo_params, graph_type='chimera', n=n)

        pegasus_results = evaluate_embedding(problem, qubo_params, graph_type='pegasus', n=n)

        all_chimera_results += [[graph_size] + row for row in chimera_results]
        all_pegasus_results += [[graph_size] + row for row in pegasus_results]

        chimera_df = pd.DataFrame(all_chimera_results, columns=['graph_size', 'n_qubits', 'max_chain', 'mean_chain'])
        pegasus_df = pd.DataFrame(all_pegasus_results, columns=['graph_size', 'n_qubits', 'max_chain', 'mean_chain'])
        chimera_df.to_csv("chimera_results.csv")
        pegasus_df.to_csv("pegasus_results.csv")

def evaluate_embedding(problem, qubo_params, graph_type, n=5):
    all_results = []
    for i in range(n):
        print(graph_type, i, end='\r')
        results = get_embedding_params(problem, qubo_params, graph_type)
        all_results.append(results)
    return all_results


def get_embedding_params(problem, qubo_params, graph_type):
    if graph_type == 'chimera':
        graph = dnx.chimera_graph(16, 16, 4)
    elif graph_type == 'pegasus':
        graph = dnx.pegasus_graph(15)
    qubo = problem.get_qubo_dict(**qubo_params)
    try:
        embedding = find_embedding(qubo, graph.edges())
    except:
        return [np.nan, np.nan, np.nan]

    if len(embedding) == 0:
        return [np.nan, np.nan, np.nan]

    all_chains = []
    chain_lenghts = []
    for node, chain in embedding.items():
        all_chains += chain
        chain_lenghts.append(len(chain))
    n_qubits = len(np.unique(all_chains))
    max_chain = np.max(chain_lenghts)
    mean_chain = np.mean(chain_lenghts)
    return [n_qubits, max_chain, mean_chain]


if __name__ == '__main__':
    main()