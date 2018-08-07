import numpy as np
import pandas as pd
import pdb
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os

def analyze_results():
    path = os.path.join("..", "results", "results_3_nodes.csv")
    data = pd.read_csv(path)

    initial_states = np.sort(data.initial_state.unique())

    data["forest_error"] = data.forest_cost - data.optimal_cost

    print("all")
    analyze_dataset(data)

    for starting_node in range(4):
        data_subset = data[data.starting_node == starting_node]
        print(starting_node)
        analyze_dataset(data_subset)


def analyze_dataset(data_subset):
    subset_size = len(data_subset)
    optimal_solutions_count = np.sum(np.isclose(data_subset["forest_error"], 0))
    correct_subset = data_subset[np.isclose(data_subset.forest_error, 0)]
    print("Size:", subset_size)
    print("Percantage of correct solutions:", optimal_solutions_count / subset_size * 100)
    print("Mean best solution probability:", np.mean(data_subset.best_sol_prob))
    print("Mean best solution probability if correct:", np.mean(correct_subset.best_sol_prob))
    print("Mean calculation time:", np.mean(data_subset.time))
    print("\n")


def main():
    analyze_results()


if __name__ == '__main__':
    main()
