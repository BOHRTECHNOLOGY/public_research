import time
from qtsp_subtree.src import TSP_utilities 
from qtsp_subtree.src.forest_tsp_solver import ForestTSPSolver
import numpy as np
import pdb
import csv
import sys
import random

def run_testing_sequence():
    number_of_nodes = 4
    file_time = time.time()
    file_tag = "starting_node_4_nodes"
    results_file = open(file_tag + "_results_" + str(file_time) + ".csv", 'w')
    angles_file = open(file_tag + "_angles_" + str(file_time) + ".csv", 'w')
    results_file.write("starting_node,initial_state,steps,tol,time,optimal_cost,forest_cost,best_sol_prob\n")

    while True:
        steps = 2
        xtol = 1e-3
        initial_state = "all"
        starting_node = random.randint(0, number_of_nodes-1)

        nodes_list = []
        for i in range(number_of_nodes):
            nodes_list.append(np.random.rand(2) * 10)
        nodes_array = np.array(nodes_list)

        run_single_tsp(nodes_array, results_file, angles_file, steps, xtol, initial_state, starting_node)
    results_file.close()


def run_single_tsp(nodes_array, results_file, angles_file, steps, xtol, initial_state, starting_node):
    params = [steps, xtol]
    print(steps, xtol)
    ftol = xtol
    start_time = time.time()
    forest_solver = ForestTSPSolver(nodes_array, steps=steps, xtol=xtol, ftol=ftol, initial_state=initial_state, starting_node=starting_node)
    
    [betas, gammas] = forest_solver.find_angles()
    print(betas)
    print(gammas)

    forest_solver.betas = betas
    forest_solver.gammas = gammas
    results = forest_solver.get_results()
    end_time = time.time()
    calculation_time = end_time - start_time

    brute_force_solution = TSP_utilities.solve_tsp_brute_force_from_given_node(nodes_array, starting_node)
    cost_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    optimal_cost = TSP_utilities.calculate_cost(cost_matrix, brute_force_solution)

    solution = forest_solver.get_solution()
    forest_cost = TSP_utilities.calculate_cost(cost_matrix, solution)
    best_solution_probability = results[0][1]

    row = [starting_node, initial_state] + params + [calculation_time] + [optimal_cost, forest_cost, best_solution_probability]
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
    run_testing_sequence()


if __name__ == '__main__':
    main()
