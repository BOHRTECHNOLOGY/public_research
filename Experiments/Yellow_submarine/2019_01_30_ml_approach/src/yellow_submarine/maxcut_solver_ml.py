import strawberryfields as sf
from strawberryfields.ops import *
import numpy as np
from qmlt.tf import CircuitLearner
from qmlt.tf.helpers import make_param
import itertools
from collections import Counter
import pdb
import tensorflow as tf
from collections import namedtuple
from strawberryfields.decompositions import takagi

ParametrizedGate = namedtuple('ParametrizedGate', 'gate qumodes params')

class MaxCutSolver():
    """This method allows to embed graphs as """
    def __init__(self, learner_params, training_params, adj_matrices, gates_structure, log=None):
        self.learner_params = learner_params
        self.learner_params['loss'] = self.loss_function
        self.learner_params['regularizer'] = self.regularizer
        self.training_params = training_params
        self.gates_structure = gates_structure
        self.adj_matrices = adj_matrices

        interferometer_matrix = \
        np.array(
            [[1, -1, 1, -1],
            [1, 1, 1, 1],
            [-1, -1, 1, 1],
            [1, -1, -1, 1]
            ]) / 2
        self.interferometer_matrix = interferometer_matrix

        self.n_qumodes = self.adj_matrices[0].shape[0]

        self.learner_params['circuit'] = self.create_circuit_evaluator
        self.learner = CircuitLearner(adj_matrices=self.adj_matrices, hyperparams=self.learner_params, model_dir=training_params['model_dir'])
        self.final_params = None

        if log is None:
            self.log = {}
        else:
            self.log = log

    def train_and_evaluate_circuit(self, verbose=True):
        self.learner.train_circuit(steps=self.training_params['steps'], tensors_to_log=self.log)
        final_params = self.learner.get_circuit_parameters()
        
        if verbose:
            for name, value in final_params.items():
                print("Parameter {} has the final value {}.".format(name, value))

        for gate in self.gates_structure:
            for gate_element_id in range(len(gate)):
                if gate_element_id < 2:
                    continue
                gate_name = gate[gate_element_id]['name']
                for param_name in final_params:
                    if gate_name in param_name:
                        final_value = final_params[param_name]
                        gate[gate_element_id]['constant'] = final_value
                        break

        self.final_params = final_params
        all_results = []
        circuit_outputs = []
        cost_values = []
        for adj_matrix in self.adj_matrices:
            circuit_output = self.get_circuit_output(adj_matrix)
            
            cost_tensor = self.loss_function([circuit_output], [adj_matrix])
            init = tf.global_variables_initializer()
            with tf.Session() as sess:
                sess.run(init)
                circuit_output = sess.run(circuit_output)
                cost_value = sess.run(cost_tensor)
            circuit_outputs.append(circuit_output)
            cost_values.append(cost_value)
            if verbose:
                print("Total cost:", cost_value)
        return cost_values, circuit_outputs
 
    def create_circuit_evaluator(self, adj_matrix):
        return self.get_circuit_output(adj_matrix)

    def build_circuit(self, adj_matrix):
        params_counter = 0
        number_of_layers = 2
        all_sgates = [[]] * number_of_layers
        all_dgates = [[]] * number_of_layers
        all_kgates = [[]] * number_of_layers
        all_vgates = [[]] * number_of_layers

        for gate_structure in self.gates_structure:
            current_layer = int(gate_structure[2]['name'].split('_')[-1][0])
            if gate_structure[0] is Sgate:
                current_gate = ParametrizedGate(gate_structure[0], gate_structure[1], [make_param(**gate_structure[2]), make_param(**gate_structure[3])])
                all_sgates[current_layer].append(current_gate)
            if gate_structure[0] is Dgate:
                current_gate = ParametrizedGate(gate_structure[0], gate_structure[1], [make_param(**gate_structure[2]), make_param(**gate_structure[3])])
                all_dgates[current_layer].append(current_gate)
            if gate_structure[0] is Kgate:
                current_gate = ParametrizedGate(gate_structure[0], gate_structure[1], [make_param(**gate_structure[2])])
                all_kgates[current_layer].append(current_gate)
            if gate_structure[0] is Vgate:
                current_gate = ParametrizedGate(gate_structure[0], gate_structure[1], [make_param(**gate_structure[2])])
                all_vgates[current_layer].append(current_gate)


        eng, q = sf.Engine(self.n_qumodes)
        rl, U = takagi(adj_matrix)
        initial_squeezings = np.tanh(rl)

        with eng:
            for i ,squeeze_value in enumerate(initial_squeezings):
                Sgate(squeeze_value) | i

            Interferometer(U) | q
            for layer in range(number_of_layers):
                sgates = all_sgates[layer]
                dgates = all_dgates[layer]
                kgates = all_kgates[layer]
                vgates = all_vgates[layer]

                if len(sgates) != 0:
                    Interferometer(self.interferometer_matrix) | q
                    for gate in sgates:
                        gate.gate(gate.params[0], gate.params[1]) | gate.qumodes


                if len(dgates) != 0:
                    Interferometer(self.interferometer_matrix) | q
                    for gate in dgates:
                        gate.gate(gate.params[0], gate.params[1]) | gate.qumodes


                for gate in kgates:
                    gate.gate(gate.params[0]) | gate.qumodes

                for gate in vgates:
                    gate.gate(gate.params[0]) | gate.qumodes


        circuit = {}
        circuit['eng'] = eng
        circuit['q'] = q

        return circuit

    def get_circuit_output(self, adj_matrix, test=False):
        circuit = self.build_circuit(adj_matrix)
        eng = circuit['eng']
        encoding = []
        state = eng.run('tf', cutoff_dim=self.training_params['cutoff_dim'], eval=False)
        all_probs = state.all_fock_probs()
        circuit_output = all_probs
        trace = tf.identity(tf.abs(state.trace()), name='trace')
        tf.summary.scalar(name='trace', tensor=trace)
        
        if test:
            init = tf.global_variables_initializer()
            with tf.Session() as sess:
                sess.run(init)
                all_probs_num = sess.run(all_probs)
            pdb.set_trace()

        return circuit_output

    def loss_function(self, circuit_outputs, adj_matrices):
        result = tf.constant(0, dtype=tf.float32)
        for circuit_output, adj_matrix in zip(circuit_outputs, adj_matrices):
            result = tf.add(result, self.single_loss_function(circuit_output, adj_matrix))
        return result

    def single_loss_function(self, circuit_output, adj_matrix):
        cost_tensor = tf.constant(self.prepare_cost_array(adj_matrix), dtype=tf.float32, name='cost_tensor')
        weighted_cost_tensor = tf.multiply(cost_tensor, circuit_output)
        result = tf.reduce_sum(weighted_cost_tensor)
        result = tf.multiply(result, tf.constant(-1.0))
        return result

    def regularizer(self, regularized_params):
        return tf.nn.l2_loss(regularized_params)

    def prepare_cost_array(self, adj_matrix):
        cutoff = self.training_params['cutoff_dim']
        cost_array = np.zeros([cutoff] * self.n_qumodes)
        for indices in np.ndindex(cost_array.shape):
            cost_array[indices] = calculate_cost_once(np.clip(indices,0,1), adj_matrix)
        return cost_array


def calculate_cost_once(encoding, adj_matrix):
    cost_value = 0
    for i in range(len(encoding)):
        for j in range(len(encoding)):
            cost_value += 0.5 * adj_matrix[i][j] * (encoding[i] - encoding[j])**2
    return cost_value


def assess_all_solutions_clasically(adj_matrix):
    all_possible_solutions = list(itertools.product([0, 1], repeat=len(adj_matrix)))
    for solution in all_possible_solutions:
        print(solution, calculate_cost_once(solution, adj_matrix))
