import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import pdb

dwave_shift_1 = -0.2
dwave_shift_2 = 0
dwave_shift_3 = 0.2

def main():
    data_path = os.path.join('..', 'results')
    data = pd.read_csv(os.path.join(data_path, 'benchmark.csv'), index_col=False)
    create_plot_for_values(data, 'sample_percentage_1', shift=dwave_shift_1, plot_style='r.')
    create_plot_for_values(data, 'sample_percentage_2', shift=dwave_shift_2, plot_style='g.')
    create_plot_for_values(data, 'sample_percentage_3', shift=dwave_shift_3, plot_style='b.')
    postprocess_and_save_plot("[%]", "Percentage of samples for best solution", os.path.join(data_path, "sample_percentage.png"))

    create_error_plot(data)
    postprocess_and_save_plot("ratio", "Ratio of errors", os.path.join(data_path, "errors.png"))

def create_plot_for_values(data, col_name, shift=0, plot_style='.'):
    number_of_nodes_list = []
    results_list = []
    for number_of_nodes in data.num_nodes.unique():
        data_subset = data[data.num_nodes == number_of_nodes]
        for problem_num in data_subset.problem_num.unique():
            values = data_subset[data_subset.problem_num == problem_num][col_name]
            number_of_nodes_list.append([number_of_nodes] * len(values))
            results_list.append(values)
    number_of_nodes_list = add_scatter(number_of_nodes_list, shift)

    plt.semilogy(number_of_nodes_list, results_list, plot_style, alpha=0.8)
    plt.plot([],[],plot_style,label=col_name)

def create_error_plot(data):
    number_of_nodes_list = []
    dwave_error_list_1 = []
    dwave_error_list_2 = []
    dwave_error_list_3 = []
    qbsolv_error_list = []
    for number_of_nodes in data.num_nodes.unique():
        data_subset = data[data.num_nodes == number_of_nodes]
        for problem_num in data_subset.problem_num.unique():
            dwave_costs_1 = data_subset[data_subset.problem_num == problem_num]['dwave_cost_1']
            dwave_costs_2 = data_subset[data_subset.problem_num == problem_num]['dwave_cost_2']
            dwave_costs_3 = data_subset[data_subset.problem_num == problem_num]['dwave_cost_3']
            qbsolv_costs = data_subset[data_subset.problem_num == problem_num]['qbsolv_cost']
            optimal_costs = data_subset[data_subset.problem_num == problem_num]['optimal_cost']
            dwave_error_1 = (dwave_costs_1 - optimal_costs) / optimal_costs
            dwave_error_2 = (dwave_costs_2 - optimal_costs) / optimal_costs
            dwave_error_3 = (dwave_costs_3 - optimal_costs) / optimal_costs
            qbsolv_error = (qbsolv_costs - optimal_costs) / optimal_costs
            number_of_nodes_list.append([number_of_nodes] * len(optimal_costs))
            dwave_error_list_1.append(dwave_error_1)
            dwave_error_list_2.append(dwave_error_2)
            dwave_error_list_3.append(dwave_error_3)
            qbsolv_error_list.append(qbsolv_error)

    number_of_nodes_list = np.array(add_scatter(number_of_nodes_list))

    dwave_error_list =np.array(dwave_error_list_1).round(6)
    dwave_zero_values = np.ma.masked_where(dwave_error_list != 0, dwave_error_list)
    dwave_non_zero_values = np.ma.masked_where(dwave_error_list == 0, dwave_error_list)
    plt.plot(number_of_nodes_list + dwave_shift_1, dwave_zero_values, '.', color=[1, 0.5, 0.5], alpha=0.8)
    plt.plot(number_of_nodes_list + dwave_shift_1, dwave_non_zero_values, '.', color=[1, 0, 0], alpha=0.8)

    dwave_error_list =np.array(dwave_error_list_2).round(6)
    dwave_zero_values = np.ma.masked_where(dwave_error_list != 0, dwave_error_list)
    dwave_non_zero_values = np.ma.masked_where(dwave_error_list == 0, dwave_error_list)
    plt.plot(number_of_nodes_list + dwave_shift_2, dwave_zero_values, '.', color=[0.5, 1, 0], alpha=0.8)
    plt.plot(number_of_nodes_list + dwave_shift_2, dwave_non_zero_values, '.', color=[0, 1, 0], alpha=0.8)

    dwave_error_list =np.array(dwave_error_list_3).round(6)
    dwave_zero_values = np.ma.masked_where(dwave_error_list != 0, dwave_error_list)
    dwave_non_zero_values = np.ma.masked_where(dwave_error_list == 0, dwave_error_list)
    plt.plot(number_of_nodes_list + dwave_shift_3, dwave_zero_values, '.', color=[0, 1, 1], alpha=0.8)
    plt.plot(number_of_nodes_list + dwave_shift_3, dwave_non_zero_values, '.', color=[0, 0, 1], alpha=0.8)



    plt.plot([],[], 'r.', label="D-Wave 1")
    plt.plot([],[], 'g.', label="D-Wave 2")
    plt.plot([],[], 'b.', label="D-Wave 3")

    plt.legend()
    
def add_scatter(x, shift=0):
    scatter_size = 0.18
    if len(np.array(x).shape)==1:
        x = np.array(x) + (0.5 - np.random.random(len(x))) * scatter_size + shift
    else:
        for i in range(len(x)):
            x[i] = np.array(x[i]) + (0.5 - np.random.random(len(x[i]))) * scatter_size + shift
    return x

def postprocess_and_save_plot(ylabel, title, filepath):
    plt.xlabel("number of nodes")
    plt.ylabel(ylabel)
    plt.legend(bbox_to_anchor=(0, -0.2), loc="lower left", ncol=2)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()    


if __name__ == '__main__':
    main()