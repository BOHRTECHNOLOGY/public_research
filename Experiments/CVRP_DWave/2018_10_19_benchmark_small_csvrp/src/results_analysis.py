import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import pdb

ortools_shift = -0.2
qbsolv_shift = 0
dwave_shift = 0.2

def main():
    data_path = os.path.join('..', 'results')
    data = pd.read_csv(os.path.join(data_path, 'benchmark.csv'), index_col=False)
    create_plot_for_function(data, 'dwave_time', np.std, plot_style='m.', label="D-Wave total")
    create_plot_for_function(data, 'dwave_qpu_time', np.std, plot_style='b.', label="D-Wave QPU")
    create_plot_for_function(data, 'qbsolv_time', np.std, plot_style='g.', label="QBSolv")
    create_plot_for_function(data, 'ortools_time', np.std, plot_style='r.', label="ORTools")
    postprocess_and_save_plot("std [s]", "std of calculation time", os.path.join(data_path, "std_times_all.png"))

    create_plot_for_function(data, 'dwave_qpu_time', np.std, plot_style='b.', label="D-Wave QPU")
    create_plot_for_function(data, 'qbsolv_time', np.std, plot_style='g.', label="QBSolv")
    create_plot_for_function(data, 'ortools_time', np.std, plot_style='r.', label="ORTools")
    postprocess_and_save_plot("std [s]", "std of calculation time", os.path.join(data_path, "std_times_calculation.png"))

    create_plot_for_function(data, 'dwave_qpu_time', np.mean, plot_style='b.', label="D-Wave QPU")
    create_plot_for_function(data, 'qbsolv_time', np.mean, plot_style='g.', label="QBSolv")
    create_plot_for_function(data, 'ortools_time', np.mean, plot_style='r.', label="ORTools")
    postprocess_and_save_plot("time [s]", "mean calculation time", os.path.join(data_path, "calculation_times.png"))

    create_plot_for_values(data, 'sample_percentage', plot_style='b.')
    postprocess_and_save_plot("[%]", "Percentage of samples for best solution", os.path.join(data_path, "sample_percentage.png"))

    create_error_plot(data)
    postprocess_and_save_plot("ratio", "Ratio of errors", os.path.join(data_path, "errors.png"))

def create_plot_for_function(data, col_name, function, plot_style='.', label='time'):
    number_of_nodes_list = []
    results_list = []
    for number_of_nodes in data.num_nodes.unique():
        data_subset = data[data.num_nodes == number_of_nodes]
        for problem_num in data_subset.problem_num.unique():
            func_result = function(data_subset[data_subset.problem_num == problem_num][col_name])
            number_of_nodes_list.append(number_of_nodes)
            results_list.append(func_result)
    number_of_nodes_list = add_scatter(number_of_nodes_list)

    plt.plot(number_of_nodes_list, results_list, plot_style, alpha=0.8)
    plt.plot([], [], plot_style, label=label)
    
def create_plot_for_values(data, col_name, plot_style='.'):
    number_of_nodes_list = []
    results_list = []
    for number_of_nodes in data.num_nodes.unique():
        data_subset = data[data.num_nodes == number_of_nodes]
        for problem_num in data_subset.problem_num.unique():
            values = data_subset[data_subset.problem_num == problem_num][col_name]
            number_of_nodes_list.append([number_of_nodes] * len(values))
            results_list.append(values)
    number_of_nodes_list = add_scatter(number_of_nodes_list)

    plt.semilogy(number_of_nodes_list, results_list, plot_style, alpha=0.8)

def create_error_plot(data):
    number_of_nodes_list = []
    dwave_error_list = []
    qbsolv_error_list = []
    ortools_error_list = []
    for number_of_nodes in data.num_nodes.unique():
        data_subset = data[data.num_nodes == number_of_nodes]
        for problem_num in data_subset.problem_num.unique():
            dwave_costs = data_subset[data_subset.problem_num == problem_num]['dwave_cost']
            qbsolv_costs = data_subset[data_subset.problem_num == problem_num]['qbsolv_cost']
            ortools_costs = data_subset[data_subset.problem_num == problem_num]['ortools_cost']
            optimal_costs = data_subset[data_subset.problem_num == problem_num]['optimal_cost']
            dwave_error = (dwave_costs - optimal_costs) / optimal_costs
            qbsolv_error = (qbsolv_costs - optimal_costs) / optimal_costs
            ortools_error = (ortools_costs - optimal_costs) / optimal_costs
            number_of_nodes_list.append([number_of_nodes] * len(optimal_costs))
            dwave_error_list.append(dwave_error)
            qbsolv_error_list.append(qbsolv_error)
            ortools_error_list.append(ortools_error)

    number_of_nodes_list = np.array(add_scatter(number_of_nodes_list))
    ortools_error_list = np.array(ortools_error_list).round(6)
    ortools_zero_values = np.ma.masked_where(ortools_error_list != 0, ortools_error_list)
    ortools_non_zero_values = np.ma.masked_where(ortools_error_list == 0, ortools_error_list)
    plt.plot(number_of_nodes_list + ortools_shift , ortools_zero_values, '.', color=[1, 0.5, 0.5], alpha=0.8)
    plt.plot(number_of_nodes_list + ortools_shift, ortools_non_zero_values, '.', color=[1, 0, 0], alpha=0.8)

    qbsolv_error_list = np.array(qbsolv_error_list).round(6)
    qbsolv_zero_values = np.ma.masked_where(qbsolv_error_list != 0, qbsolv_error_list)
    qbsolv_non_zero_values = np.ma.masked_where(qbsolv_error_list == 0, qbsolv_error_list)
    plt.plot(number_of_nodes_list + qbsolv_shift, qbsolv_zero_values, '.', color=[0.5, 1, 0], alpha=0.8)
    plt.plot(number_of_nodes_list + qbsolv_shift, qbsolv_non_zero_values, '.', color=[0, 1, 0], alpha=0.8)

    dwave_error_list = np.array(dwave_error_list).round(6)
    dwave_zero_values = np.ma.masked_where(dwave_error_list != 0, dwave_error_list)
    dwave_non_zero_values = np.ma.masked_where(dwave_error_list == 0, dwave_error_list)
    plt.plot(number_of_nodes_list + dwave_shift, dwave_zero_values, '.', color=[0, 1, 1], alpha=0.8)
    plt.plot(number_of_nodes_list + dwave_shift, dwave_non_zero_values, '.', color=[0, 0, 1], alpha=0.8)


    plt.plot([],[], 'r.', label="ORTools")
    plt.plot([],[], 'g.', label="QBSolv")
    plt.plot([],[], 'b.', label="D-Wave")
    plt.legend()
    
def add_scatter(x):
    scatter_size = 0.18
    if len(np.array(x).shape)==1:
        x = np.array(x) + (0.5 - np.random.random(len(x))) * scatter_size
    else:
        for i in range(len(x)):
            x[i] = np.array(x[i]) + (0.5 - np.random.random(len(x[i]))) * scatter_size
    return x

def postprocess_and_save_plot(ylabel, title, filepath):
    plt.xlabel("number of nodes")
    plt.ylabel(ylabel)
    plt.legend(bbox_to_anchor=(0, -0.2), loc="lower left", ncol=4)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()    


if __name__ == '__main__':
    main()