import numpy as np
import pandas as pd
import pdb
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os

def analyze_results():
    path = os.path.join("..", "results", "test_series_2_full.csv")
    data = pd.read_csv(path)

    steps = np.sort(data.steps.unique())
    tols = np.sort(data.tol.unique())[::-1]
    cases = np.sort(data.case.unique())

    data["forest_error"] = data.forest_cost - data.optimal_cost
    for case in cases:
        case_subset = data[(data.case==case)]
        print("Case:", case)
        analyze_dataset(case_subset)

    for case in cases:
        for step in steps:
            for tol in tols:
                data_subset = case_subset[(case_subset.steps==step) & (case_subset.tol==tol)]
                print("case, step, tol:", case, step, tol)
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
