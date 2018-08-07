import time
from qtsp_subtree.src import TSP_utilities 
from qtsp_subtree.src.forest_tsp_solver import ForestTSPSolver
import numpy as np
import pdb
import csv
import sys
import random

def run_testing_sequence(number_of_nodes=3, is_random=False, all_ones=-2):
    nodes_array = np.array([[0, 0], [0,5], [5,5], [5,0]])
    nodes_array = nodes_array[:number_of_nodes]
    file_time = time.time()
    results_file = open("results_all_ones_minus_"+ str(np.abs(all_ones))+"_" + str(file_time) + ".csv", 'w')
    angles_file = open("angles_all_ones_minus_"+ str(np.abs(all_ones))+"_" + str(file_time) + ".csv", 'w')

    results_file.write("steps,tol,valid_prob,almost_valid_prob,time,best_valid,best_almost_valid\n")
    csv_writer = csv.writer(results_file)
    csv_writer_angles = csv.writer(angles_file)
    possible_steps = [3, 2, 1]
    possible_xtol = [1e-4, 1e-3, 1e-2]
    if is_random:
        while True:
            steps = random.choice(possible_steps)
            xtol = random.choice(possible_xtol)
            run_single_tsp(nodes_array, csv_writer, csv_writer_angles, steps, xtol, all_ones=all_ones)
    else:
        for steps in possible_steps:
            for xtol in possible_xtol:
                for i in range(10):
                    run_single_tsp(nodes_array, csv_writer, csv_writer_angles, steps, xtol, all_ones=all_ones)
    results_file.close()

def run_single_tsp(nodes_array, csv_writer, csv_writer_angles, steps, xtol, all_ones=0):
    params = [steps, xtol]
    print(steps, xtol)
    ftol = xtol
    start_time = time.time()
    forest_solver = ForestTSPSolver(nodes_array, steps=steps, xtol=xtol, ftol=ftol, all_ones_coefficient=all_ones)
    [betas, gammas] = forest_solver.find_angles()
    print(betas)
    print(gammas)
    # betas = np.array([1.40268584, 2.74136728, 2.76970739])
    # gammas = np.array([1.41543072, 1.56411558, 2.29933395])

    forest_solver.betas = betas
    forest_solver.gammas = gammas
    results = forest_solver.get_results()
    end_time = time.time()
    calculation_time = end_time - start_time
    metrics = calculate_metrics(results, calculation_time)
    row = params + metrics
    print(row)
    if csv_writer is not None:
        csv_writer.writerow(row)
        csv_writer_angles.writerow(row)
        csv_writer_angles.writerow(betas)
        csv_writer_angles.writerow(gammas)
        csv_writer_angles.writerow("\n")
    sys.stdout.flush()


def check_if_solution_is_valid(solution):
    solution = list(solution)
    number_of_nodes = int(np.sqrt(len(solution)))
    time_groups = [solution[number_of_nodes*i:number_of_nodes*(i+1)] for i in range(number_of_nodes)]
    for group in time_groups:
        if np.sum(group) != 1:
            return False
        if time_groups.count(group) != 1:
            return False
    return True


def check_if_solution_is_almost_valid(solution):
    solution = list(solution)
    number_of_nodes = int(np.sqrt(len(solution)))
    time_groups = [solution[number_of_nodes*i:number_of_nodes*(i+1)] for i in range(number_of_nodes)]
    if [1, 1, 1] not in time_groups:
        return False
    for group in time_groups:
        if not (np.sum(group) != 1 or np.sum(group) != number_of_nodes):
            return False
        if np.sum(group) == 1 and time_groups.count(group) != 1:
            return False
    return True


def calculate_metrics(results, calculation_time):
    valid_results_probability = 0
    almost_valid_results_probability = 0
    for entry in results:
        if check_if_solution_is_valid(entry[0]):
            valid_results_probability += entry[1]
        elif check_if_solution_is_almost_valid(entry[0]):
            almost_valid_results_probability += entry[1]

    best_result = results[0][0]
    best_result_valid = check_if_solution_is_valid(best_result)
    best_result_almost_valid = check_if_solution_is_almost_valid(best_result)
    return [valid_results_probability, almost_valid_results_probability, calculation_time, best_result_valid, best_result_almost_valid]

def main():
    run_testing_sequence(number_of_nodes=3, is_random=False, all_ones=-2)
    # nodes_array = np.array([[0,0], [0, 5], [0, 10]])
    # run_single_tsp(nodes_array, None, 3, 1e-4, 2)


if __name__ == '__main__':
    main()
