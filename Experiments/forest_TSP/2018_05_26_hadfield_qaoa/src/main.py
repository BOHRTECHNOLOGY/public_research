import time
from qtsp_subtree.src import TSP_utilities 
from qtsp_subtree.src.forest_tsp_solver import ForestTSPSolver
from qtsp_subtree.src.forest_tsp_solver import visualize_cost_matrix
import numpy as np
import pdb
import csv
import sys
import random

def run_testing_sequence(number_of_nodes=3, is_random=True):
    all_nodes_arrays = []
    # 1D cases:
    # ARRAY 1: [0 - 1 - 2], symmetrical
    nodes_array_1 = np.array([[0, 0], [0, 10], [0, 20]])
    all_nodes_arrays.append(nodes_array_1)
    # # ARRAY 2: [0 - 2 - 1], symmetrical
    nodes_array_2 = np.array([[0, 0], [0, 20], [0, 10]])
    all_nodes_arrays.append(nodes_array_2)
    # # ARRAY 3: [2 - 1 - 0], symmetrical
    nodes_array_3 = np.array([[0, 10], [0, 20], [0, 0]])
    all_nodes_arrays.append(nodes_array_3)
    # # ARRAY 4: [0 - 1 - 2] assymetrical
    nodes_array_4 = np.array([[0, 0], [0, 1], [0, 10]])
    all_nodes_arrays.append(nodes_array_4)
    # # ARRAY 5: [2 - 0 - 1] assymetrical
    nodes_array_5 = np.array([[0, 1], [0, 0], [0, 10]])
    all_nodes_arrays.append(nodes_array_5)

    # # 2D cases:
    # # ARRAY 1: equilateral triangle
    nodes_array_6 = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])
    all_nodes_arrays.append(nodes_array_6)
    # # ARRAY 2: symetrical triangle [0 - 2 - 1]
    nodes_array_7 = np.array([[-5, 0], [5, 0], [0, 1]])
    all_nodes_arrays.append(nodes_array_7)
    # # ARRAY 3: asymetrical triangle [0 - 2 - 1]
    nodes_array_8 = np.array([[0, 0], [15, 0], [0, 1]])
    all_nodes_arrays.append(nodes_array_8)
    # # ARRAY 4: random array
    nodes_array_9 = None
    all_nodes_arrays.append(nodes_array_9)

    file_time = time.time()
    file_tag = "test_series_2"
    results_file = open(file_tag + "_results_" + str(file_time) + ".csv", 'w')
    angles_file = open(file_tag + "_angles_" + str(file_time) + ".csv", 'w')
    results_file.write("case,steps,tol,time,optimal_cost,forest_cost,best_sol_prob\n")

    possible_steps = [2, 1]
    possible_xtol = [1e-3, 1e-2]
    possible_cases = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    while True:
        steps = random.choice(possible_steps)
        xtol = random.choice(possible_xtol)
        case = random.choice(possible_cases)
        nodes_array = all_nodes_arrays[case]
        if nodes_array is None:
            nodes_list = []
            for i in range(number_of_nodes):
                nodes_list.append(np.random.rand(2) * 10)
            scaled_nodes_array = np.array(nodes_list)
        else:
            scaled_nodes_array = nodes_array * np.random.rand() * 5 + 5 * (np.random.rand() - 0.5)
        run_single_tsp(scaled_nodes_array, results_file, angles_file, steps, xtol, case)
    results_file.close()

def run_single_tsp(nodes_array, results_file, angles_file, steps, xtol, case):
    params = [steps, xtol]
    print(steps, xtol)
    ftol = xtol
    start_time = time.time()
    forest_solver = ForestTSPSolver(nodes_array, steps=steps, xtol=xtol, ftol=ftol)
    
    [betas, gammas] = forest_solver.find_angles()
    print(betas)
    print(gammas)

    forest_solver.betas = betas
    forest_solver.gammas = gammas
    results = forest_solver.get_results()
    end_time = time.time()
    calculation_time = end_time - start_time

    brute_force_solution = TSP_utilities.solve_tsp_brute_force(nodes_array)
    cost_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    optimal_cost = TSP_utilities.calculate_cost(cost_matrix, brute_force_solution)

    solution = forest_solver.get_solution()
    forest_cost = TSP_utilities.calculate_cost(cost_matrix, solution)
    best_solution_probability = results[0][1]

    row = [case] + params + [calculation_time] + [optimal_cost, forest_cost, best_solution_probability]
    print(row)
    print("Results", results)

    csv_writer = csv.writer(results_file)
    csv_writer_angles = csv.writer(angles_file)

    csv_writer.writerow(row)
    csv_writer_angles.writerow(row)
    csv_writer_angles.writerow(nodes_array)
    csv_writer_angles.writerow(results)
    csv_writer_angles.writerow(betas)
    csv_writer_angles.writerow(gammas)
    csv_writer_angles.writerow("\n")
    results_file.flush()
    angles_file.flush()
    sys.stdout.flush()


def main():
    run_testing_sequence(number_of_nodes=3)


if __name__ == '__main__':
    main()
