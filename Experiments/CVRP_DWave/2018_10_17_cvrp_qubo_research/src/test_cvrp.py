"""Check solutions of CVRP problem for varying range of capacity constant used in QUBO."""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'vrp_solver_subtree/src'))
import argparse
from itertools import product
import logging
from networkx import complete_graph
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore
from utilities import compute_all_cvrp_solutions, partitions
from dwave_engine import DWaveEngine
from problem import Problem


COST_MAGNITUDE = 0
NUMBER_OF_NODES = 7
NUMBER_OF_TRIES = 10
NUMBER_OF_GRAPHS = 10
COST_CONSTANT = 1
CONSTRAINT_CONSTANT = 6
CHAIN_STRENGTH = 8
CAPACITY_CONSTANTS = (0, 1, 2, 4, 6)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o',
                        help='Where to store output (default: dwave_cvrp.csv',
                        default='dwave_cvrp.csv',
                        type=str)
    logging.basicConfig(level='INFO')
    logger = logging.getLogger('tes_tsp.main')

    args = parser.parse_args()

    vehicles = pd.DataFrame(columns=['vehicle_id', 'capacity'])
    vehicles['vehicle_id'] = range(3)
    vehicles['capacity'] = 7
    outposts = pd.DataFrame(columns=['outpost_id', 'load'])
    outposts["outpost_id"] = range(NUMBER_OF_NODES)
    outposts["load"] = [0, 2, 3, 1, 2, 3, 2]

    records = []
    engine = DWaveEngine.default()
    for i, graph in enumerate(generate_graphs(NUMBER_OF_NODES, COST_MAGNITUDE, NUMBER_OF_GRAPHS), 1):
        logger.info('Starting computation for graph number %d', i)
        result = time_it(engine, outposts, vehicles, graph, NUMBER_OF_TRIES)
        records = records + result

    pd.DataFrame(records, columns=['capacity_constant', 'cost', 'percentile', 'relative_error']).to_csv(args.output)

def time_it(engine, outposts, vehicles, graph, number_of_tries):
    logger = logging.getLogger('test_tsp.perform_experiment')
    records = []
    all_solutions = compute_all_cvrp_solutions(outposts, vehicles, graph)
    all_costs = [cost for _, cost in all_solutions]

    for capacity_constant in CAPACITY_CONSTANTS:
        for _ in range(number_of_tries):
            best_solution = None
            best_cost = None # does not matter
            for partition in partitions(len(outposts), len(vehicles)):

                problem = Problem(vehicles=vehicles,
                                  outposts=outposts,
                                  vehicles_partition=partition,
                                  graph=graph,
                                  starting_point=0,
                                  use_capacity_constraints=True)
                max_weight = max(dict(graph.edges).items(), key=lambda x: x[1]['weight'])[1]['weight']

                resultset = engine.sample(problem,
                                          cost_constant=COST_CONSTANT * max_weight,
                                          constraint_constant=CONSTRAINT_CONSTANT * max_weight,
                                          chain_strength=CHAIN_STRENGTH * max_weight,
                                          capacity_constraint_constant=capacity_constant * max_weight)
                solution = resultset.best_solution
                if solution is not None:
                    cost = solution.total_cost()
                    if best_solution is None or cost < best_cost:
                        best_solution = solution
                        best_cost = cost
            if best_solution is None:
                logger.warning('No valid solution found by D-Wave')
            else:
                percentile = percentileofscore(all_costs, cost, kind='strict')
                relative_error = (cost - all_costs[0]) / all_costs[0]
                if relative_error < 0:
                    import pdb
                    pdb.set_trace()
                records.append((capacity_constant, cost, percentile, relative_error))
    return records

def generate_graphs(number_of_nodes, order_of_magnitude, number_of_graphs):
    for _ in range(number_of_graphs):
        yield create_random_graph(number_of_nodes, order_of_magnitude)

def create_random_graph(number_of_nodes, order_of_magnitude):
    graph = complete_graph(number_of_nodes)
    for i in range(number_of_nodes):
        for j in range(i+1, number_of_nodes):
            weight = np.random.rand() * 10
            graph[i][j]['weight'] = weight
            graph[j][i]['weight'] = weight
    return graph

if __name__ == '__main__':
    main()
