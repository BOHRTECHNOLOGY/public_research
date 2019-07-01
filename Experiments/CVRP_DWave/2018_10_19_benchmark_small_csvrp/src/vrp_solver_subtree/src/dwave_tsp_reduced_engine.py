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
        self.numruns = 1000
        self.starting_point = starting_point
        self.qubo_dict = self.construct_qubo(self.create_cost_matrix())
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
            print(record)
            solution = self.route_from_sample(sample)
            if solution is not None:
                print(solution, calculate_cost_of_solution(solution, self.graph))
            if solution is None:
                failed_distribution[tuple(sample)] = (record.energy, record.num_occurrences)
            else:
                distribution[tuple(solution)] = (record.energy, record.num_occurrences)
                if record.energy <= min_energy:
                    self.solution = solution
                    min_energy = record.energy
        self.distribution = distribution
        self.failed_distribution = failed_distribution

    def construct_qubo(self, cost_matrix):
        """Construct QUBO for TSP problem given cost matrix.

        :param cost_matrix: matrix M such that M[i,j] is a cost of travel between
         i-th and j-th node. It is assumed that this matrix is symmetric and
         contains only nonnegative entries.
        :type cost_matrix: numpy.ndarray
        :returns: mapping (i, j) -> coefficient, where (i, j) are encoded QUBO's
         variables. The returned mapping is always symmetric.
        :rtype: defaultdict(float)
        """

        # We subtract 1, since we have a fixed starting point.
        number_of_nodes = cost_matrix.shape[0] - 1
        map_indices = partial(map_indices_to_qubit, num_nodes=number_of_nodes)
        qubo_dict = defaultdict(float)
        reduced_cost_matrix = np.delete(cost_matrix, self.starting_point, axis=0)
        reduced_cost_matrix = np.delete(reduced_cost_matrix, self.starting_point, axis=1)

        # First add row constraints: for every step there must be precisely one node we visit
        for step in range(number_of_nodes):
            for i in range(number_of_nodes):
                qubo_dict[(map_indices(step, i), map_indices(step, i))] += -self.constraint_constant
                for j in range(i+1, number_of_nodes):
                    qubo_dict[(map_indices(step, i), map_indices(step, j))] += 2 * self.constraint_constant

        # Second add column constraints: every node should be visited at precisely one step
        for node in range(number_of_nodes):
            for i in range(number_of_nodes):
                qubo_dict[(map_indices(i, node), map_indices(i, node))] += -self.constraint_constant
                for j in range(i+1, number_of_nodes):
                    qubo_dict[(map_indices(i, node), map_indices(j, node))] += 2 * self.constraint_constant

        # Third: add the objective function. Note that it includes penalty for nonexisting routes
        for i in range(number_of_nodes):
            for j in range(number_of_nodes):
                if i != j:
                    for step in range(number_of_nodes - 1):
                        cost = reduced_cost_matrix[i, j]
                        next_step = (step+1) % number_of_nodes
                        if step < next_step:
                            qubo_dict[(map_indices(step, i), map_indices(next_step, j))] += self.cost_constant * cost
                        else:
                            qubo_dict[(map_indices(next_step, i), map_indices(step, j))] += self.cost_constant * cost

        # Fourth: encode information about cost to the first node from beginning and end of the route
        for i in range(number_of_nodes):
            cost_vector = cost_matrix[self.starting_point]
            cost_vector = np.delete(cost_vector, self.starting_point, axis=0)
            cost = cost_vector[i]
            qubo_dict[(map_indices(0, i), map_indices(0, i))] += self.cost_constant * cost
            qubo_dict[(map_indices(number_of_nodes-1, i), map_indices(number_of_nodes-1, i))] += self.cost_constant * cost

        qubo_matrix = np.zeros((number_of_nodes**2, number_of_nodes**2))
        qubo_matrix[:] = np.nan
        for key in qubo_dict:
            qubo_matrix[key] = qubo_dict[key]
        pdb.set_trace()
        return qubo_dict


    def route_from_sample(self, sample):
        """Given the solution of QUBO and number of nodes, read corresponding route.

        :param sample: sample obtained from the solver. The expected format is
         a 0-1 sequence where i-th element is i-th qubit's value.
        :type sample: sequence
        :returns: sequence route such that route[i] contains number of node
         that should be visited in i-th step. Does not contain final destination (i.e. for
         a route 0 -> 1 -> 2 -> 0 the return value is [0, 1, 2]). If given sample does not encode
         a valid solution None will be returned.

        .. note::
           This function does not check whether all of the constraints are satisfied,
           and if solution is found that violates some of them, the behaviour is
           not well defined.
        """
        number_of_nodes = int(np.sqrt(len(sample)))
        route = [-1 for _ in range(number_of_nodes)]

        for qubit_idx, value in enumerate(sample):
            if value  > 0:
                step, node = map_qubit_to_indices(qubit_idx, number_of_nodes)
                if node >= self.starting_point:
                    node += 1
                route[step] = node
        if -1 in route or len(set(route)) != number_of_nodes:
            return None
        route.insert(0, self.starting_point)
        route.append(self.starting_point)
        return route


def map_indices_to_qubit(step, node, num_nodes):
    return step * num_nodes + node

def map_qubit_to_indices(qubit_no, num_nodes):
    """This reverses map_index_to_qubit."""
    return divmod(qubit_no, num_nodes)

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
