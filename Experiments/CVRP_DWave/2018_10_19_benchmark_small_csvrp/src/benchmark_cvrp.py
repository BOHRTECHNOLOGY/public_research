"""Script for running benchmark."""
import argparse
from networkx import complete_graph
import numpy as np
import pandas as pd
import yaml
from benchmarking_engine import benchmark_cvrp
from problem import Problem
from vrp_solver_subtree.src.utilities import generate_outposts, generate_vehicles


def main():
    """Entrypoint of this script."""
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                       help='file with benchmark config')
    parser.add_argument('--output',
                        help='file to store benchmarking results.',
                        default='benchmark.csv')

    args = parser.parse_args()

    with open(args.input) as input_file:
        config = yaml.load(input_file)

    display_config(config)
    if isinstance(config['num_nodes'], list):
        num_nodes_list = config['num_nodes']
    else:
        num_nodes_list = [config['num_nodes']]
    results_list = []
    for num_nodes in num_nodes_list:
        print("Solving for ", num_nodes, "nodes")
        problem_source = generate_problems(num_graphs=config['num_graphs'],
                                           num_nodes=num_nodes,
                                           order_of_magnitude=config['edges_magnitude'])

        results = benchmark_cvrp(problem_source=problem_source,
                                num_tries=config['num_tries'],
                                ortools_config=config['ortools_config'],
                                dwave_config=config['dwave_config'])
        results['num_nodes'] = num_nodes
        results_list.append(results)
    
        print("\n")
        final_results = pd.concat(results_list)
        reordered_columns = ['num_nodes'] + list([a for a in final_results.columns if a != 'num_nodes'])
        final_results = final_results.reindex(columns=(reordered_columns))
        final_results.to_csv(args.output, index=False)


def generate_problems(num_graphs, num_nodes, order_of_magnitude):

    vehicles = pd.DataFrame(columns=['vehicle_id', 'capacity'])
    vehicles['vehicle_id'] = [0]
    vehicles['capacity'] = [num_nodes]

    for i in range(num_graphs):
        graph = create_random_graph(num_nodes, order_of_magnitude)
        outposts = generate_outposts(len(graph))
        vehicles = generate_vehicles(outposts)
        yield Problem(vehicles=vehicles,
                      outposts=outposts,
                      vehicles_partition=[len(graph)-1],
                      graph=graph,
                      starting_point=0,
                      use_capacity_constraints=True)


def create_random_graph(number_of_nodes, order_of_magnitude):
    graph = complete_graph(number_of_nodes)
    for i in range(number_of_nodes):
        graph.node[i]['load'] = 1
        for j in range(i+1, number_of_nodes):
            weight = np.random.rand() * 10 ** order_of_magnitude
            graph[i][j]['weight'] = weight
            graph[j][i]['weight'] = weight
    return graph

def display_config(config):
    dw_config = config['dwave_config']
    or_config = config['ortools_config']
    print('----------------------------------')
    print('Benchmark configuration:')
    print('----------------------------------')
    print(' number of nodes: {}'.format(config['num_nodes']))
    print(' number of graphs: {}'.format(config['num_graphs']))
    print(' number of tries for each graph: {}'.format(config['num_tries']))
    print('----------------------------------')
    print('D-Wave specific configuration:')
    print('----------------------------------')
    print(' cost constant: {}'.format(dw_config.get('cost_constant', 'unspecified')))
    print(' constraint constant: {}'.format(dw_config.get('constraint_constant', 'unspecified')))
    print(' capacity constraint constant: {}'.format(dw_config.get('capacity_constraint_constant', 'unspecified')))
    print(' chain strength: {}'.format(dw_config.get('chain_strength'), 'unspecified'))
    print('----------------------------------')
    print('ortools specific configuration:')
    print('----------------------------------')
    print(' calculation time: {}'.format(config['ortools_config'].get('calculation_time', 5)))

if __name__ == '__main__':
    main()
