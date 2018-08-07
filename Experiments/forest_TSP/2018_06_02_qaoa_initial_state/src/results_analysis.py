import numpy as np
import pandas as pd
import pdb
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os

def analyze_results():
    path = os.path.join("..", "results", "initial_states_results.csv")
    data = pd.read_csv(path)

    # These lines are for adding the data from the previous experiment and filtering them appropriately.
    old_data_path = os.path.join("..", "results", "2018_05_26_hadfield_qaoa.csv")
    old_data = pd.read_csv(old_data_path)
    old_data["initial_state"] = "[0, 1, 2]"
    old_data = old_data[(old_data.tol==0.001) & (old_data.steps==2)]
    data = pd.concat([data, old_data])

    cases = np.sort(data.case.unique())
    initial_states = np.sort(data.initial_state.unique())

    data["forest_error"] = data.forest_cost - data.optimal_cost
    for state in initial_states:
        state_subset = data[(data.initial_state==state)]
        print("Initial state:", state)
        analyze_dataset(state_subset)

    for case in cases:
        print("_"*20)
        for state in initial_states:
            case_subset = data[(data.case==case)]
            data_subset = case_subset[case_subset.initial_state==state]
            print("case, initial_state:", case, state)
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
