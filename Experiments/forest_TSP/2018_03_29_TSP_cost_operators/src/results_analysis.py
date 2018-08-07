import numpy as np
import pandas as pd
import pdb
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os

def analyze_results_for_tsp_testing():
    path_1 = os.path.join("..", "results", "phase_3_results_weight_10_standard_case.csv")
    path_2 = os.path.join("..", "results", "phase_3_results_weight_100_standard_case.csv")
    data_1 = pd.read_csv(path_1)
    data_2 = pd.read_csv(path_2)

    steps = np.sort(data_1.steps.unique())
    tols = np.sort(data_1.tol.unique())[::-1]

    for step in steps:
        for tol in tols:
            
            data_1_subset = data_1[(data_1.steps==step) & (data_1.tol==tol)]
            data_2_subset = data_2[(data_2.steps==step) & (data_2.tol==tol)]

            perc_valid_solutions_1 = np.mean(data_1_subset.best_valid)
            perc_valid_solutions_2 = np.mean(data_2_subset.best_valid)
            valid_prob_1 = np.mean(data_1_subset.valid_prob)
            valid_prob_2 = np.mean(data_2_subset.valid_prob)
            valid_prob_1_std = np.std(data_1_subset.valid_prob)
            valid_prob_2_std = np.std(data_2_subset.valid_prob)
            valid_solutions_1 = data_1_subset[data_1_subset.best_valid]
            valid_solutions_2 = data_2_subset[data_2_subset.best_valid]
            mean_best_sol_prob_1 = np.mean(valid_solutions_1.best_sol_prob)
            mean_best_sol_prob_2 = np.mean(valid_solutions_2.best_sol_prob)
            mean_best_sol_prob_1_std = np.std(valid_solutions_1.best_sol_prob)
            mean_best_sol_prob_2_std = np.std(valid_solutions_2.best_sol_prob)
            mean_error_1 = np.mean(valid_solutions_1.forest_cost - valid_solutions_1.optimal_cost)
            mean_error_2 = np.mean(valid_solutions_2.forest_cost - valid_solutions_2.optimal_cost)

            print("params", step, tol)
            print("number of elements in datasets:", len(data_1_subset), len(data_2_subset))
            print("Percentage of best solution being valid", perc_valid_solutions_1, perc_valid_solutions_2)
            print_result_with_std("Mean count of valid solutions", valid_prob_1, valid_prob_1_std, valid_prob_2, valid_prob_2_std)
            print_result_with_std("Mean count of best solutions", mean_best_sol_prob_1, mean_best_sol_prob_1_std, mean_best_sol_prob_2, mean_best_sol_prob_2_std)
            print("Mean count of best solutions when best is valid", np.mean(valid_solutions_1.best_sol_prob), np.mean(valid_solutions_2.best_sol_prob))
            print("Mean count of valid solutions when best is valid", np.mean(valid_solutions_1.valid_prob), np.mean(valid_solutions_2.valid_prob))
            print("Mean error:", mean_error_1, mean_error_2)
            print("Mean time:", np.mean(data_1_subset.time), np.mean(data_2_subset.time))
            print("")
    

    pdb.set_trace()

def print_result_with_std(text, val1, std1, val2, std2):
    val1 = np.round(val1, 3)
    val2 = np.round(val2, 3)
    std1 = np.round(std1, 3)
    std2 = np.round(std2, 3)
    print(text, str(val1)+"("+str(std1)+")", str(val2)+"("+str(std2)+")")

def analyze_results_for_all_ones_testing():
    path_1 = os.path.join("..", "results", "results_3_nodes_minus_1_v2.csv")
    path_2 = os.path.join("..", "results", "results_3_nodes_minus_2_v2.csv")
    data_1 = pd.read_csv(path_1)
    data_2 = pd.read_csv(path_2)
    valid_prob_1 = np.mean(data_1.valid_prob)
    valid_prob_2 = np.mean(data_2.valid_prob)
    best_valid_1 = np.mean(data_1.best_valid)
    best_valid_2 = np.mean(data_2.best_valid)
    print("minus 1")
    print(valid_prob_1, best_valid_1)

    print("minus 2")
    print(valid_prob_2, best_valid_2)
    pdb.set_trace()

def analyze_results_for_parameters_testing():
    data_path = os.path.join("..", "results", "phase_3_results_weight_100_standard_case.csv")
    data = pd.read_csv(data_path)

    aggregation_list = []

    for steps, data_steps in data.groupby('steps'):
        print("Number of steps:", steps)
        for tol, group in data_steps.groupby('tol'):
            results = [steps, tol, np.mean(group.time), np.mean(group.valid_prob), np.sum(group.best_valid) / len(group), len(group)]
            print(results)
            aggregation_list.append(results)

    aggregation_list = np.array(aggregation_list)

    fig, ax = plt.subplots()
    ax.set_yscale('log')
    scatter_plot = ax.scatter(aggregation_list[:,0], aggregation_list[:, 1], s=200, c=aggregation_list[:, 2], cmap='plasma')
    cbar = fig.colorbar(scatter_plot)
    ax.set_xlabel("steps")
    ax.set_ylabel("tol")
    ax.set_title("Calculation time for different parameters")
    plt.savefig("calculation_time.png")
    plt.clf()

    fig, ax = plt.subplots()
    ax.set_yscale('log')
    scatter_plot = ax.scatter(aggregation_list[:,0], aggregation_list[:, 1], s=200, c=aggregation_list[:, 3], cmap='plasma')
    cbar = fig.colorbar(scatter_plot)
    ax.set_xlabel("steps")
    ax.set_ylabel("tol")
    ax.set_title("Mean count of valid result for different parameters")
    plt.savefig("valid_result_count.png")
    plt.clf()

    fig, ax = plt.subplots()
    ax.set_yscale('log')
    scatter_plot = ax.scatter(aggregation_list[:,0], aggregation_list[:, 1], s=200, c=aggregation_list[:, 4], cmap='plasma')
    cbar = fig.colorbar(scatter_plot)
    ax.set_xlabel("steps")
    ax.set_ylabel("tol")
    ax.set_title("Percentage of correct results for different parameters")
    plt.savefig("correct_results_perc.png")
    plt.clf()


def main():
    # analyze_results_for_tsp_testing()
    analyze_results_for_parameters_testing()
    # analyze_results_for_all_ones_testing()

if __name__ == '__main__':
    main()
