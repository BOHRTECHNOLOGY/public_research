"""Module containing solution-related functionallities."""
import logging
from collections import OrderedDict, namedtuple
import numpy as np
import pandas as pd

PartialSolution = namedtuple('PartialSolution', 'vehicle_id route cost')

class Solution(list):

    def total_cost(self):
        """Calculate total cost of this solution."""
        return sum(partial_solution.cost for partial_solution in self)

    def to_dataframe(self):
        """Convert this solution to DataFrame."""
        return pd.DataFrame(list(self), columns=("vehicle_id", "route", "cost"))

class ResultSet(object):
    """Representation of all results obtained from solver."""

    def __init__(self, raw_record, problem):
        self.problem = problem
        self.raw_record = raw_record
        self._failed_samples = None
        self._successful_samples = None
        self._best_solution = None

    @property
    def failed_samples(self):
        """Return dictionary of failed samples."""
        if self._failed_samples is None or self._successful_samples is None:
            self._decode_all_solutions()
        return self._failed_samples

    @property
    def successful_samples(self):
        if self._failed_samples is None or self._successful_samples is None:
            self._decode_all_solutions()
        return self._successful_samples

    @property
    def best_solution(self):
        if self._failed_samples is None or self._successful_samples is None:
            self._decode_all_solutions()
        return self._best_solution

    def _decode_all_solutions(self):
        logger = logging.getLogger('Solution._decode_solutions')
        self._failed_samples = OrderedDict()
        self._successful_samples = OrderedDict()
        # We use OrderedDict here to remember order at which solutions are inserted
        # That way we will iterate over them in the same order as they were
        # returned by solver (in particular it should be sorted by energy).u
        best_solution = None
        min_energy = None
        for record in self.raw_record:
            sample = record[0]
            logger.debug('Parsing record: %s', record)
            solution = self.decode_solution_from_sample(sample)
            if solution is None:
                self._failed_samples[tuple(sample)] = (record.energy, record.num_occurrences)
            else:
                if logger.isEnabledFor(logging.getLevelName('DEBUG')):
                    logger.debug('Found feasible solution: ')
                    for _, route, cost in solution:
                        logger.debug('%s, %s', route, cost)
                self._successful_samples[tuple(sample)] = (record.energy, record.num_occurrences)
                if min_energy is None or record.energy <= min_energy:
                    best_solution = solution
                    min_energy = record.energy
        self._best_solution = best_solution

    def decode_solution_from_sample(self, sample):
        """Decode solution from given bitstring if it represents a valid route.

        Parses a sample (bitstring of 0s and 1s representing the solution),
        and evaluates if it represents valid solution. If it does, calculates the cost
        and returns the solution.

        :param sample: sample obtained from the solver. The expected format is
         a 0-1 sequence where i-th element is i-th qubit's value.
        :type sample: sequence
        :returns solution: list of lists. Each list consists of vehicle_id, route
         (ordered list of visited nodes) and cost associated with this route.
        :rtype: [[int, list, float], ] or None
        """
        solution = Solution()
        starting_qubit = 0
        number_of_nodes = int(np.sqrt(len(sample)))
        for i, row in self.problem.vehicles.iterrows():
            vehicle_id = row.vehicle_id
            vehicle_capacity = row.capacity
            current_partition = self.problem.vehicles_partition[i]
            sample_subset = sample[starting_qubit:starting_qubit + current_partition * number_of_nodes]
            route = self.route_from_sample_subset(sample_subset, number_of_nodes, vehicle_capacity)
            starting_qubit += current_partition * number_of_nodes
            if route is None:
                return None
            if len(route) != 2 or route[0] != self.problem.starting_point or route[i] != self.problem.starting_point:
                cost = calculate_cost_of_route(route, self.problem.graph)
                solution.append(PartialSolution(vehicle_id, route, cost))
            # In case when given vehicle is not being used we do nothing

        return solution

    def route_from_sample_subset(self, sample_subset, number_of_nodes, vehicle_capacity=1):
        """Creates corresponding route given the subset of solution of QUBO and number of nodes,

        :param sample_subset: sample_subset obtained from the solver. The expected format is
         a 0-1 sequence where i-th element is i-th qubit's value.
        :type sample_subset: sequence
        :param number_of_nodes: number of outposts excluding depot.
        :type number_of_nodes: int
        :returns: sequence route such that route[i] contains number of node
         that should be visited in i-th step.
        If given sample_subset does not encode a valid solution None will be returned.

        .. note::
           This method does not check whether all of the constraints are satisfied,
           and if solution is found that violates some of them, the behaviour is
           not well defined.
        """
        route = []
        partition_size = int(len(sample_subset)/number_of_nodes)
        for qubit_idx, value in enumerate(sample_subset):
            if value > 0:
                _, node = self.problem.map_qubit_to_indices(qubit_idx)
                if node >= self.problem.starting_point:
                    node += 1
                route.append(node)
        if len(set(route)) != partition_size or len(route) != partition_size:
            return None
        if self.problem.use_capacity_constraints:
            outpost_loads = list(self.problem.outposts.load)
            total_load = 0
            for node in route:
                total_load += outpost_loads[node]
            if total_load > vehicle_capacity:
                return None

        route.insert(0, self.problem.starting_point)
        route.append(self.problem.starting_point)
        return route

def calculate_cost_of_route(route, graph):
    """Calculate the total cost of given route.

    :param route: sequence such that route[i] contains index of node that
     should be visited in i-th step.
    :type route: sequence
    :param graph: graph representing all connections between outposts
    :type graph: networkx graph
    :returns: total cost of given route, i.e. sum of all weights of edges visited
     along the route.
    """
    if route is None:
        return np.nan
    total_cost = 0
    for i in range(len(route) - 1):
        edge = (route[i], route[i+1])
        total_cost += graph.edges[edge]['weight']
    return total_cost
