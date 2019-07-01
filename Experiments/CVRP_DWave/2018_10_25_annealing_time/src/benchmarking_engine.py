"""Engine for benchmarking ortools vs D-Wave."""
from collections import namedtuple
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'vrp_solver_subtree/src'))
from time import time
from dwave_engine import DWaveEngine
from qbsolv_engine import DWaveEngine as QBSolvEngine
from ortools_engine import calculate_routes
import numpy as np
import pandas as pd
import utilities

Record = namedtuple('Record', 'problem_num try_num dwave_time_1 dwave_qpu_time_1 dwave_time_2 dwave_qpu_time_2 dwave_time_3 dwave_qpu_time_3 qbsolv_time sample_percentage_1 sample_percentage_2 sample_percentage_3 dwave_cost_1 dwave_cost_2 dwave_cost_3 qbsolv_cost optimal_cost')

def benchmark_tsp(problem_source, num_tries, ortools_config, dwave_config):
    """Benchmark D-Wave vs ortools for given problems and configuration.

    :param problem_source: an interable with problems to solve
    :type problem source: iterable of Problem
    :param num_tries: how many times to try to solve given problem
    :type num_tries: int
    :param ortools_config: configuration for ortools. Currently only the key
     'calculation_time` is used, but can be extended should we need to add more
     parameters.
    :type ortools_config; mapping
    :param dwave_config: configuration used with D-Wave solver. Can contains any entries
     corresponding to keyword arguments used by DWaveEngine.solve method.
    :type dwave_config: mapping
    :returns: DataFrame with columns: problem_num, try_num, dwave_time, ortools_time,
     dwave_cost, ortools_cost. If any of engines failed to provide a solution fo any of the
     problem/try a np.nan is used instead of a corresponding cost.
    :rtype: :py:class:`pandas.DataFrame`
    """
    dwave_engine = DWaveEngine.default()
    qbsolv_engine = QBSolvEngine.default()
    results = []
    ortools_calculation_time = ortools_config.get('calculation_time', 5)
    for i, problem in enumerate(problem_source, 1):
        for j in range(1, num_tries+1):
            print('Benchmarking problem {0}, try {1}.'.format(i, j))
            start = time()
            dwave_config['annealing_time'] = 20
            dwave_solution_1, number_of_samples_1, info_1 = dwave_engine.solve(problem, **dwave_config)
            dwave_time_1 = time() - start

            start = time()
            dwave_config['annealing_time'] = 40
            dwave_solution_2, number_of_samples_2, info_2 = dwave_engine.solve(problem, **dwave_config)
            dwave_time_2 = time() - start

            start = time()
            dwave_config['annealing_time'] = 60
            dwave_solution_3, number_of_samples_3, info_3 = dwave_engine.solve(problem, **dwave_config)
            dwave_time_3 = time() - start

            start = time()
            qbsolv_solution = qbsolv_engine.solve(problem, **dwave_config)
            qbsolv_time = time() - start

            if number_of_samples_1 is not None:
                sample_percentage_1 = number_of_samples_1 / dwave_config['num_reads'] * 100
            else:
                sample_percentage_1 = np.nan

            if number_of_samples_2 is not None:
                sample_percentage_2 = number_of_samples_2 / dwave_config['num_reads'] * 100
            else:
                sample_percentage_2 = np.nan

            if number_of_samples_3 is not None:
                sample_percentage_3 = number_of_samples_3 / dwave_config['num_reads'] * 100
            else:
                sample_percentage_3 = np.nan


            # start = time()
            # ortools_solution = calculate_routes(outposts=problem.outposts,
            #                                     vehicles=problem.vehicles,
            #                                     graph=problem.graph,
            #                                     starting_point=problem.starting_point,
            #                                     calculation_time=ortools_calculation_time)
            # ortools_time = time() - start
            optimal_cost = utilities.compute_all_tsp_solutions(problem.graph)[0][1]
            record = Record(
                problem_num=i,
                try_num=j,
                dwave_time_1=dwave_time_1,
                dwave_qpu_time_1=info_1['timing']['total_real_time']/10e6,
                dwave_time_2=dwave_time_2,
                dwave_qpu_time_2=info_2['timing']['total_real_time']/10e6,
                dwave_time_3=dwave_time_3,
                dwave_qpu_time_3=info_3['timing']['total_real_time']/10e6,

                qbsolv_time=qbsolv_time,
                sample_percentage_1=sample_percentage_1,
                sample_percentage_2=sample_percentage_2,
                sample_percentage_3=sample_percentage_3,

                dwave_cost_1=np.nan if dwave_solution_1 is None else dwave_solution_1.total_cost(),
                dwave_cost_2=np.nan if dwave_solution_2 is None else dwave_solution_2.total_cost(),
                dwave_cost_3=np.nan if dwave_solution_3 is None else dwave_solution_3.total_cost(),

                qbsolv_cost=np.nan if qbsolv_solution is None else qbsolv_solution.total_cost(),
                optimal_cost=optimal_cost)
            results.append(record)
    return pd.DataFrame(results)
