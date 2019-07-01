"""Module containing problem-related functionallities."""
from collections import namedtuple, defaultdict
from itertools import product
import numpy as np

# Fields required for constructing instances of the problem
FIELDS = 'vehicles outposts vehicles_partition graph starting_point, use_capacity_constraints'

_Problem = namedtuple('_Problem', FIELDS)
_Problem.__new__.__defaults__ = (None,)

class Problem(_Problem):
    """Representation of problem to solve."""



    def get_qubo_dict(self, cost_constant, constraint_constant, capacity_constraint_constant):
        """Get QUBO representation of this problem provided constants to use.

        :param cost_constant: constant to scale cost part of QUBO
        :type cost_constant: float
        :param constraint_constant: constant to scale constraint part of QUBO
        :type cost constant: float
        :param capacity_constraint: constant to scale capacity constraint part of QUBO
        :type capacity_constraint: float
        :returns: dictionary representing Quadratic Unconstrained Optimization Problem
         representation of this problem. The dict maps pairs (i, j) of indices to the
         coefficient corresponding to product q_i * q_j.
        """
        cost_matrix = self.create_cost_matrix()

        # We subtract 1, since we have a fixed starting point.
        number_of_nodes = cost_matrix.shape[0] - 1
        qubo_dict = defaultdict(float)
        map_indices = self.map_indices_to_qubit
        reduced_cost_matrix = np.delete(cost_matrix, self.starting_point, axis=0)
        reduced_cost_matrix = np.delete(reduced_cost_matrix, self.starting_point, axis=1)

        # First add row constraints: for every step there must be precisely one node we visit
        for step, i in product(range(number_of_nodes), range(number_of_nodes)):
            qubo_dict[(map_indices(step, i), map_indices(step, i))] += -constraint_constant
            for j in range(i+1, number_of_nodes):
                qubo_dict[(map_indices(step, i), map_indices(step, j))] += 2 * constraint_constant

        # Second add column constraints: every node should be visited at precisely one step
        for node, i in product(range(number_of_nodes), range(number_of_nodes)):
            qubo_dict[(map_indices(i, node), map_indices(i, node))] += -constraint_constant
            for j in range(i+1, number_of_nodes):
                qubo_dict[(map_indices(i, node), map_indices(j, node))] += 2 * constraint_constant

        starting_step = 0
        for vehicle_index, row in self.vehicles.iterrows():
            partition_size = self.vehicles_partition[vehicle_index]
            vehicle_capacity = row.capacity
            if partition_size == 0:
                continue
            final_step = starting_step + partition_size

            # Third: add the objective function. Note that it includes penalty for nonexisting routes
            for i, j in product(range(number_of_nodes), range(number_of_nodes)):
                if i != j:
                    for step in range(starting_step, final_step - 1):
                        cost = reduced_cost_matrix[i, j]
                        next_step = (step+1) % number_of_nodes
                        if step < next_step:
                            qubo_dict[(map_indices(step, i), map_indices(next_step, j))] += cost_constant * cost
                        else:
                            qubo_dict[(map_indices(next_step, i), map_indices(step, j))] += cost_constant * cost

            # Fourth: encode information about cost to the first node from beginning and end of the route
            for i in range(number_of_nodes):
                cost_vector = cost_matrix[self.starting_point]
                cost_vector = np.delete(cost_vector, self.starting_point, axis=0)
                cost = cost_vector[i]
                qubo_dict[(map_indices(starting_step, i), map_indices(starting_step, i))] += cost_constant * cost
                qubo_dict[(map_indices(final_step - 1, i), map_indices(final_step - 1, i))] += cost_constant * cost

            if self.use_capacity_constraints:
                # Fifth: encode capacity constraints
                outpost_loads = list(self.outposts.load)
                outpost_loads = np.delete(outpost_loads, self.starting_point, axis=0)
                for i, j in product(range(number_of_nodes), range(number_of_nodes)):
                    for t_1 in range(starting_step, final_step - 1):
                        for t_2 in range(starting_step, final_step - 1):
                            if i != j and t_1 != t_2:
                                index_1 = map_indices(t_1, i)
                                index_2 = map_indices(t_2, j)
                                loads_coefficient = outpost_loads[i] * outpost_loads[j] / vehicle_capacity**2
                                qubo_dict[(index_1, index_2)] += capacity_constraint_constant * loads_coefficient

            starting_step += partition_size

        # This is code is for debugging purposes only
        qubo_matrix = np.zeros((number_of_nodes**2, number_of_nodes**2))
        qubo_matrix[:] = np.nan
        for key in qubo_dict:
            qubo_matrix[key] = qubo_dict[key]
        return qubo_dict

    def create_cost_matrix(self):
        """Calculate the cost matrix for this problem.

        :returns: matrix, where each cell represents the cost for travelling between outpost i and j.
                  If the route is not present, the cost is set to sum of all the weights in graph.
        :rtype: numpy array
        """
        num_outposts = len(self.outposts)
        cost_matrix = np.zeros((num_outposts, num_outposts))
        sum_of_all_costs = sum(weight for _i, _j, weight in self.graph.edges(data='weight'))
        for i in range(num_outposts):
            for j in range(i + 1, num_outposts):
                if j in self.graph[i]:
                    cost_matrix[i, j] = self.graph[i][j]['weight']
                    cost_matrix[j, i] = self.graph[i][j]['weight']
                else:
                    # to prevent travelling along nonexisting routes
                    cost_matrix[i, j] = sum_of_all_costs
                    cost_matrix[j, i] = sum_of_all_costs
        return cost_matrix

    def map_indices_to_qubit(self, step, node):
        """Map given step and node to qubit index."""
        return step * (len(self.outposts) - 1) + node


    def map_qubit_to_indices(self, qubit_no):
        """This reverses map_indices_to_qubit."""
        return divmod(qubit_no, (len(self.outposts) - 1))
