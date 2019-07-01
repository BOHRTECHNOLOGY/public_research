"""Engine for solving VRP with D-Wave."""
import itertools
import logging
from collections import defaultdict
from functools import partial
from dwave.system.samplers import DWaveSampler           # Library to interact with the QPU
from dwave.system.composites import EmbeddingComposite   # Library to embed our problem onto the QPU physical graph
import numpy as np
import pandas as pd
from problem import Problem
from solution import ResultSet


class DWaveEngine(object):
    """Class for solving Vehicle Routing Problem using DWave.

    The represantation used here is as follows:
    For given set of vehicles, we specify how many outposts each vehicle should visit.
    Then the problem is solved and each part of the bitstring received from D-Wave machine
    represents one vehicle.

    Attributes (arguments):
        verbose (bool): toggles printing more information during run
        use_capacity_constraints (bool): toggles use of capacity constraints. If True we solve CVRP, if False - VRP.
        outposts (DataFrame): stores information about outposts. For more information see readme.
        vehicles (DataFrame): stores information about vehicles. For more information see readme.
        graph (nx graph): stores information about graph. For more information see readme.
        vehicles_partition ([int]): specifies how many outposts each vehicle should visit
        qubo_dict

    Attributes (kwargs):
        chainstrength (int): specifies how strong are interactions between physical qubits creating
                            one logical qubit on D-Wave machine. should be much higher than other values.
        constraint_constant (int): specifies the weight of constraints in QUBO problem. Should be much higher than cost values.
        cost_constant (int): specifies the weight of the cost values.
        numruns (int): how many times program will be run on D-Wave machine.
        starting_point (int): specifies which outpost is depot. By default it's one with index 0.

    Attributes:
        qubo_dict (dict): dictionary with QUBO represention of the problem.
        sapi_token (string): token needed to connect to D-Wave machine.
        url (string): endpoint for connecting to D-Wave machine.
        solution (list): list with the following structure: [ [vehicle_id, route, cost], ].
                         If no solution was found it's None.
        distribution (dict): dictionary, where keys represent samples from D-Wave
                             and values are tuples: (energy, num_occurrences).
                             It stores only valid solutions.
        failed_distribution (dict): same as distribution, but for samples representing invalid solutions.
    """
    DEFAULT_SAPI_URL = 'https://cloud.dwavesys.com/sapi'

    DEFAULT_SOLVER_PARAMS = {
        'chain_strength': 800,
        'num_reads': 1000}

    DEFAULT_QUBO_PARAMS = {
        'cost_constant': 10,
        'constraint_constant': 400,
        'capacity_constraint_constant': 200}

    def __init__(self, sampler):
        self.sampler = sampler

    def solve(self, problem, **params):
        """Solve given VRP problem.

        :param problem: definition of the problem to solve
        :type problem: py:class:`problem.Problem`
        """
        raw_solutions = self._get_raw_solutions(problem, **params)
        return ResultSet(raw_solutions.record, problem).best_solution

    def sample(self, problem, **params):
        raw_solutions = self._get_raw_solutions(outposts, vehicles, graph, vehicles_partition, **params)
        return ResultSet(raw_solutions.record, problem)

    def _get_raw_solutions(self, problem, **params):
        logger = logging.getLogger(__name__)
        solver_params = self._extract_kwargs(params, self.DEFAULT_SOLVER_PARAMS)
        qubo_params = self._extract_kwargs(params, self.DEFAULT_QUBO_PARAMS)
        logger.debug('Using solver parameters: %s', solver_params)
        logger.debug('Using qubo parameters: %s', qubo_params)
        return self.sampler.sample_qubo(problem.get_qubo_dict(**qubo_params), **solver_params)

    @classmethod
    def default(cls):
        with open('dwave_credentials.txt') as token_file:
            sapi_token = token_file.read()
        sampler = EmbeddingComposite(DWaveSampler(token=sapi_token, endpoint=cls.DEFAULT_SAPI_URL))
        return cls(sampler)

    @staticmethod
    def _extract_kwargs(kwargs, defaults):
        return {key: kwargs.get(key, value) for key, value in defaults.items()}

def calculate_routes(outposts, vehicles, graph, starting_point=0, **kwargs):
    """Finds solution to VRP problem using D-Wave machine.

    :param outposts: dataframe containing information about outposts. See readme for more details.
    :type outposts: pandas DataFrame
    :param vehicles: dataframe containing information about vehicles. See readme for more details.
    :type vehicles: pandas DataFrame
    :param graph: graph representing all connection between outposts
    :type graph: networkx graph
    :param starting_point: specifies which outpost is depot. By default it's one with index 0.
    :type starting_point: int
    """
    number_of_vehicles = len(vehicles)
    number_of_nodes = len(outposts) - 1

    # Source: https://stackoverflow.com/questions/28965734/general-bars-and-stars
    vehicles_partitions = []
    total_load = outposts.load.sum()
    capacities = list(vehicles.capacity)
    for combination in itertools.combinations(range(number_of_nodes+number_of_vehicles-1), number_of_vehicles-1):
        current_partition = [b-a-1 for a, b in zip((-1,) + combination, combination+(number_of_nodes+number_of_vehicles-1,))]
        current_partition = sorted(current_partition)
        if current_partition not in vehicles_partitions:
            vehicle_presence_vector = [0 if number==0 else 1 for number in current_partition]
            total_capacity = np.dot(vehicle_presence_vector, capacities)
            if total_capacity >= total_load:
                vehicles_partitions.append(current_partition)

    dwave_solver = DWaveEngine.default()
    if 'use_capacity_constraints' in kwargs:
        use_capacity_constraints = kwargs['use_capacity_constraints']
        del kwargs['use_capacity_constraints']
    else:
        use_capacity_constraints = True
    print("All partitions:", vehicles_partitions)
    best_solution = None
    for current_partition in vehicles_partitions:
        print("Current partition: ", current_partition)
        problem = Problem(vehicles=vehicles,
                          outposts=outposts,
                          vehicles_partition=current_partition,
                          graph=graph,
                          starting_point=starting_point,
                          use_capacity_constraints=use_capacity_constraints)
        current_solution = dwave_solver.solve(problem)
        if current_solution is None:
            print("No valid solutions found with D-Wave")
        elif best_solution is None:
            best_solution = current_solution
        else:
            current_cost = sum(sub_solution[2] for sub_solution in current_solution)
            best_cost = best_solution.total_cost
            if current_cost < best_cost:
                best_solution = current_solution

    if best_solution is None:
        return None
    return best_solution.to_dataframe()
