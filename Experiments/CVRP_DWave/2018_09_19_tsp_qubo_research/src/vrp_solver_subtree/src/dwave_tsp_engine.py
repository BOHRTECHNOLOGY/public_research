from dwave.system.samplers import DWaveSampler           # Library to interact with the QPU
from dwave.system.composites import EmbeddingComposite   # Library to embed our problem onto the QPU physical graph
import numpy as np
import pandas as pd
import itertools
from collections import defaultdict
from functools import partial
import pdb

class DWaveEngine(object):
    """
    Class for solving Travelling Salesman Problem using DWave.
    """
    def __init__(self, outposts, vehicles, graph, starting_point=0, **kwargs):
        self.outposts = outposts
        self.vehicles = vehicles
        self.graph = graph
        self.constraint_constant = kwargs.get('constraint_constant', 200)
        self.cost_constant = kwargs.get('cost_constant', 10)
        self.chainstrength = kwargs.get('chainstrength', 600)
        self.numruns = 100
        self.qubo_dict = construct_qubo(self.create_cost_matrix(),
                                        cost_mul=self.cost_constant,
                                        constraint_mul=self.constraint_constant)
        self.read_dwave_credentials()

    def create_cost_matrix(self):
        num_outposts = len(self.outposts)
        cost_matrix = np.zeros((num_outposts, num_outposts))
        sum_of_all_costs = sum(weight for _i, _j, weight in self.graph.edges(data='weight'))
        for i in range(num_outposts):
            for j in range(i+1, num_outposts):
                if j in self.graph[i]:
                    cost_matrix[i, j] = self.graph[i][j]['weight']
                    cost_matrix[j, i] = self.graph[i][j]['weight']
                else:
                    # to prevent travelling along nonexisting routes
                    cost_matrix[i, j] =  sum_of_all_costs
                    cost_matrix[j, i] =  sum_of_all_costs
        return cost_matrix

    def read_dwave_credentials(self):
        file_name = "dwave_credentials.txt"
        file = open(file_name, 'r')
        self.sapi_token = file.read()
        self.url = 'https://cloud.dwavesys.com/sapi'

    def solve_tsp(self):
        response = EmbeddingComposite(DWaveSampler(token=self.sapi_token, endpoint=self.url)).sample_qubo(self.qubo_dict, chain_strength=self.chainstrength, num_reads=self.numruns)
        self.get_solutions(response)
        return self.solution, self.distribution

    def get_solutions(self, response):
        i = 0
        distribution = {}
        self.solution = None
        failed_distribution = {}
        min_energy = self.chainstrength * 10000
        for record in response.record:
            sample = record[0]
            solution = route_from_sample(sample, len(self.outposts))
            if solution is None:
                failed_distribution[tuple(sample)] = (record.energy, record.num_occurrences)
            else:
                distribution[tuple(solution)] = (record.energy, record.num_occurrences)
                print(record.energy, min_energy)
                if record.energy <= min_energy:
                    self.solution = solution
                    min_energy = record.energy
        self.distribution = distribution
        self.failed_distribution = failed_distribution

def construct_qubo(cost_matrix, cost_mul=1, constraint_mul=8500):
    """Construct QUBO for TSP problem given cost matrix and model parameters.

    :param cost_matrix: matrix M such that M[i,j] is a cost of travel between
     i-th and j-th node. It is assumed that this matrix is symmetric and
     contains only nonnegative entries.
    :type cost_matrix: numpy.ndarray
    :param cost_mul: multiplier for coefficients of QUBO corresponding to target
     function. Defaults to 1 as in original TSP-48 notebook.
    :type cost_mul: number
    :param constraint_mul: multiplier for constraints coefficients. Defaults to
     8500 as in original TSP-48 notebook
    :type constraint_mul: number
    :returns: mapping (i, j) -> coefficient, where (i, j) are encoded QUBO's
     variables. The returned mapping is always symmetric.
    :rtype: defaultdict(float)
    """
    number_of_nodes = cost_matrix.shape[0]
    map_indices = partial(map_indices_to_qubit, num_nodes=number_of_nodes)
    qubo_dict = defaultdict(float)

    # First add row constraints: for every step there must be precisely one node we visit
    for step in range(number_of_nodes):
        for i in range(number_of_nodes):
            qubo_dict[(map_indices(step, i), map_indices(step, i))] += -constraint_mul
            for j in range(i+1, number_of_nodes):
                qubo_dict[(map_indices(step, j), map_indices(step, i))] += 2 * constraint_mul

    # Second add column constraints: every node should be visited at precisely one step
    for node in range(number_of_nodes):
        for i in range(number_of_nodes):
            qubo_dict[(map_indices(i, node), map_indices(i, node))] += -constraint_mul
            for j in range(i+1, number_of_nodes):
                qubo_dict[(map_indices(j, node), map_indices(i, node))] += 2 * constraint_mul

    # Third: add the objective function. Note that it includes penalty for nonexisting routes
    for i in range(number_of_nodes):
        for j in range(number_of_nodes):
            if i != j:
                for step in range(number_of_nodes):
                    cost = cost_matrix[i, j]
                    next_step = (step+1) % number_of_nodes
                    qubo_dict[(map_indices(step, i), map_indices(next_step, j))] += cost_mul * cost
    return qubo_dict

def map_indices_to_qubit(step, node, num_nodes):
    return step * num_nodes + node

def map_qubit_to_indices(qubit_no, num_nodes):
    """This reverses map_index_to_qubit."""
    return divmod(qubit_no, num_nodes)

def route_from_sample(sample, number_of_nodes):
    """Given the solution of QUBO and number of nodes, read corresponding route.

    :param sample: sample obtained from the solver. The expected format is
     a 0-1 sequence where i-th element is i-th qubit's value.
    :type sample: sequence
    :param number_of_nodes: number of nodes provided as the input for the problem.
     This could be deduced from sample but would require additional effort.
    :type number_of_nodes: int
    :returns: sequence route such that route[i] contains number of node
     that should be visited in i-th step. Does not contain final destination (i.e. for
     a route 0 -> 1 -> 2 -> 0 the return value is [0, 1, 2]). If given sample does not encode
     a valid solution None will be returned.

    .. note::
       This function does not check whether all of the constraints are satisfied,
       and if solution is found that violates some of them, the behaviour is
       not well defined.
    """
    route = [-1 for _ in range(number_of_nodes)]

    for qubit_idx, value in enumerate(sample):
        if value  > 0:
            step, node = map_qubit_to_indices(qubit_idx, number_of_nodes)
            route[step] = node
    if -1 in route or len(set(route)) != number_of_nodes:
        return None
    return route

def calculate_cost_of_solution(solution, graph):
    total_cost = 0
    for i in range(len(solution) - 1):
        edge = (solution[i], solution[i+1])
        total_cost += graph.edges[edge]['weight']
    return total_cost

def calculate_routes(outposts, vehicles, graph, starting_point, **kwargs):
    dwave_solver = DWaveEngine(outposts, vehicles, graph, **kwargs)
    solution, distribution = dwave_solver.solve_tsp()
    if solution is None:
        print("No valid solutions found with D-Wave")
        return None
    cost = calculate_cost_of_solution(solution, graph)
    return pd.DataFrame([[0, solution, cost]], columns=["vehicle_id", "route", "cost"])
