import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pdb
import os


def data_dir():
    return os.path.join('..', 'results')

def main():
    chimera_tsp_df = pd.read_csv(os.path.join(data_dir(), 'chimera_tsp_results.csv'))
    chimera_cvrp_df = pd.read_csv(os.path.join(data_dir(), 'chimera_cvrp_results.csv'))
    pegasus_tsp_df = pd.read_csv(os.path.join(data_dir(), 'pegasus_tsp_results.csv'))

    case = 'architecture'
    create_comparison_plot(chimera_tsp_df, pegasus_tsp_df, x='graph_size', y='n_qubits', case=case)
    create_comparison_plot(chimera_tsp_df, pegasus_tsp_df, x='graph_size', y='max_chain', case=case)
    create_comparison_plot(chimera_tsp_df, pegasus_tsp_df, x='graph_size', y='mean_chain', case=case)

    case = 'problem'
    create_comparison_plot(chimera_tsp_df, chimera_cvrp_df, x='graph_size', y='n_qubits', case=case)
    create_comparison_plot(chimera_tsp_df, chimera_cvrp_df, x='graph_size', y='max_chain', case=case)
    create_comparison_plot(chimera_tsp_df, chimera_cvrp_df, x='graph_size', y='mean_chain', case=case)


def create_comparison_plot(results_df_1, results_df_2, x, y, case):
    data_dir = os.path.join('..', 'results')
    if case == 'architecture':
        labels = ['chimera', 'pegasus']
    if case == 'problem':
        labels = ['chimera - tsp', 'chimera - cvrp']
    plt.xlabel(x)
    plt.ylabel(y)
    plt.plot(results_df_1[x], results_df_1[y], 'b.', label=labels[0], alpha=0.8)
    plt.plot(results_df_2[x], results_df_2[y], 'r.', label=labels[1], alpha=0.8)
    plt.legend()
    plt.title(y + " per " + x)
    file_name = case + "_" + y + ".png"
    plt.savefig(os.path.join(data_dir, file_name))
    plt.clf()


if __name__ == '__main__':
    main()