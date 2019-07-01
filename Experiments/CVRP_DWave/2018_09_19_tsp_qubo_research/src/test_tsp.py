"""Check solutions of TSP problem for varying range of constants used in QUBO."""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'vrp_solver_subtree/src'))
import argparse
from itertools import product
import logging
from networkx import complete_graph
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore
from utilities import compute_all_tsp_solutions
from dwave_engine import DWaveEngine
from problem import Problem


COST_MAGNITUDE = 0
NUMBER_OF_NODES = 7
NUMBER_OF_TRIES = 1
NUMBER_OF_GRAPHS = 1
CONSTRAINT_TO_COST_RATIOS = list(range(20, 100, 5))
CHAIN_TO_CONSTRAINT_RATIOS = list(range(2, 10, 1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o',
                        help='Where to store output (default: dwave_tsp.csv',
                        default='dwave_tsp.csv',
                        type=str)
    logging.basicConfig(level='INFO')
    logger = logging.getLogger('tes_tsp.main')

    args = parser.parse_args()

    vehicles = pd.DataFrame(columns=['vehicle_id', 'capacity'])
    vehicles['vehicle_id'] = [0]
    vehicles['capacity'] = [1]

    records = []
    engine = DWaveEngine.default()
    for i, graph in enumerate(generate_graphs(NUMBER_OF_NODES, COST_MAGNITUDE, NUMBER_OF_GRAPHS), 1):
        logger.info('Starting computation for graph number %d', i)
        problem = Problem(vehicles=vehicles,
                          outposts=range(len(graph)),
                          vehicles_partition=[len(graph)-1],
                          graph=graph,
                          starting_point=0,
                          use_capacity_constraints=False)
        result = time_it(engine, problem, CONSTRAINT_TO_COST_RATIOS,
                         CHAIN_TO_CONSTRAINT_RATIOS, NUMBER_OF_TRIES)
        records = records + result

    pd.DataFrame(records, columns=['const_to_cost', 'chain_to_cost', 'cost', 'percentile', 'relative_error']).to_csv(args.output)

def time_it(engine, problem, constant_to_cost_ratios, chain_to_constraint_ratios, number_of_tries):
    logger = logging.getLogger('test_tsp.perform_experiment')
    records = []
    all_solutions = compute_all_tsp_solutions(problem.graph)
    all_costs = [cost for _, cost in all_solutions]
    for const_to_cost, chain_to_const in product(constant_to_cost_ratios, chain_to_constraint_ratios):
        for _ in range(number_of_tries):
            solution = engine.solve(problem,
                                    cost_constant=10,
                                    constraint_constant=10 * const_to_cost,
                                    chain_strength=10 * const_to_cost * chain_to_const)
            if solution is None:
                logger.warning('No solution found. Nodes: %d, ratios: %f, %f',
                               len(problem.graph), const_to_cost, chain_to_const)
                continue
            cost = solution.total_cost()
            percentile = percentileofscore(all_costs, cost, kind='strict')
            relative_error = (cost - all_costs[0]) / all_costs[0]
            records.append((const_to_cost, chain_to_const, cost, percentile, relative_error))
    return records

def generate_graphs(number_of_nodes, order_of_magnitude, number_of_graphs):
    for _ in range(number_of_graphs):
        yield create_random_graph(number_of_nodes, order_of_magnitude)

def create_random_graph(number_of_nodes, order_of_magnitude):
    graph = complete_graph(number_of_nodes)
    for i in range(number_of_nodes):
        for j in range(i+1, number_of_nodes):
            weight = np.random.rand() + 10 ** order_of_magnitude
            graph[i][j]['weight'] = weight
            graph[j][i]['weight'] = weight
    return graph

if __name__ == '__main__':
    main()
