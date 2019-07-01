"""Engine for benchmarking ortools vs D-Wave."""
from collections import namedtuple
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'vrp_solver_subtree/src'))
from time import time
from dwave_engine import DWaveEngine
from ortools_engine import calculate_routes
import numpy as np
import pandas as pd

Record = namedtuple('Record', 'problem_num try_num dwave_time ortools_time dwave_cost ortools_cost')

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
    results = []
    ortools_calculation_time = ortools_config.get('calculation_time', 5)
    for i, problem in enumerate(problem_source, 1):
        for j in range(1, num_tries+1):
            print('Benchmarking problem {0}, try {1}.'.format(i, j))
            start = time()
            dwave_solution = dwave_engine.solve(problem, **dwave_config)
            dwave_time = time() - start

            start = time()
            ortools_solution = calculate_routes(outposts=problem.outposts,
                                                vehicles=problem.vehicles,
                                                graph=problem.graph,
                                                starting_point=problem.starting_point,
                                                calculation_time=ortools_calculation_time)
            ortools_time = time() - start
            record = Record(
                problem_num=i,
                try_num=j,
                dwave_time=dwave_time,
                ortools_time=ortools_time,
                dwave_cost=np.nan if dwave_solution is None else dwave_solution.total_cost(),
                ortools_cost=np.nan if ortools_solution is None else ortools_solution['cost'].sum())
            results.append(record)
    return pd.DataFrame(results)
