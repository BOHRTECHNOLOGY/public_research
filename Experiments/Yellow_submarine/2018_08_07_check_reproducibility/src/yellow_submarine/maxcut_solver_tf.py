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
    def __init__(self, learner_params, training_params, matrices, gates_structure, log=None):
        self.learner_params = learner_params
        self.learner_params['loss'] = self.loss_function
        self.learner_params['regularizer'] = self.regularizer
        self.training_params = training_params
        self.gates_structure = gates_structure
        self.adj_matrix = matrices[0]
        self.interferometer_matrix = matrices[1]
        self.n_qumodes = self.adj_matrix.shape[0]
        self.cost_array = self.prepare_cost_array()
        self.learner = None
        if log is None:
            self.log = {}
        else:
            self.log = log

    def train_and_evaluate_circuit(self):
        self.learner_params['circuit'] = self.create_circuit_evaluator
        self.learner = CircuitLearner(hyperparams=self.learner_params)
        self.learner.train_circuit(steps=self.training_params['steps'], tensors_to_log=self.log)

        final_params = self.learner.get_circuit_parameters()
        
        for name, value in final_params.items():
            if "Variable" not in name:
                print("Parameter {} has the final value {}.".format(name, value))

        for gate in self.gates_structure:
            gate_name = gate[2]['name']
            for param_name in final_params:
                if gate_name in param_name:
                    final_value = final_params[param_name]
                    gate[2]['constant'] = final_value
                    break

        all_results = []
        circuit_output = self.get_circuit_output()
        cost_tensor = self.loss_function(circuit_output)
        init = tf.global_variables_initializer()
        with tf.Session() as sess:
            sess.run(init)
            circuit_output = sess.run(circuit_output)
            cost_value = sess.run(cost_tensor)

        print("Total cost:", cost_value)
 
    def create_circuit_evaluator(self):
        return self.get_circuit_output()

    def build_circuit(self):
        params_counter = 0
        sgates = []
        dgates = []
        kgates = []
        for gate_structure in self.gates_structure:
            if gate_structure[0] is Sgate:
                sgates.append(ParametrizedGate(gate_structure[0], gate_structure[1], [make_param(**gate_structure[2])]))
            if gate_structure[0] is Dgate:
                dgates.append(ParametrizedGate(gate_structure[0], gate_structure[1], [make_param(**gate_structure[2])]))
            if gate_structure[0] is Kgate:
                kgates.append(ParametrizedGate(gate_structure[0], gate_structure[1], [make_param(**gate_structure[2])]))

        eng, q = sf.Engine(self.n_qumodes)

        rl, U = takagi(self.adj_matrix)
        initial_squeezings = np.tanh(rl)

        with eng:
            for i ,squeeze_value in enumerate(initial_squeezings):
                Sgate(squeeze_value) | i

            Interferometer(U) | q

            for gate in sgates:
                gate.gate(gate.params[0]) | gate.qumodes

            Interferometer(self.interferometer_matrix) | q

            for gate in dgates:
                gate.gate(gate.params[0]) | gate.qumodes

            Interferometer(self.interferometer_matrix) | q

            for gate in kgates:
                gate.gate(gate.params[0]) | gate.qumodes

        circuit = {}
        circuit['eng'] = eng
        circuit['q'] = q

        return circuit

    def get_circuit_output(self, test=False):
        circuit = self.build_circuit()
        eng = circuit['eng']
        encoding = []
        state = eng.run('tf', cutoff_dim=self.training_params['cutoff_dim'], eval=False)
        all_probs = state.all_fock_probs()
        circuit_output = all_probs
        trace = tf.identity(state.trace(), name='trace')
        
        if test:
            init = tf.global_variables_initializer()
            with tf.Session() as sess:
                sess.run(init)
                all_probs_num = sess.run(all_probs)
            pdb.set_trace()

        return circuit_output

    def loss_function(self, circuit_output):
        cost_tensor = tf.constant(self.cost_array, dtype=tf.float32, name='cost_tensor')
        weighted_cost_tensor = tf.multiply(cost_tensor, circuit_output)
        result = tf.reduce_sum(weighted_cost_tensor)
        result = tf.multiply(result, tf.constant(-1.0))
        return result

    def regularizer(self, regularized_params):
        return tf.nn.l2_loss(regularized_params)

    def calculate_cost_once(self, encoding):
        cost_value = 0
        for i in range(len(encoding)):
            for j in range(len(encoding)):
                cost_value += 0.5 * self.adj_matrix[i][j] * (encoding[i] - encoding[j])**2
        return cost_value

    def assess_all_solutions_clasically(self):
        all_possible_solutions = list(itertools.product([0, 1], repeat=len(self.adj_matrix)))
        for solution in all_possible_solutions:
            print(solution, self.calculate_cost_once(solution))

    def prepare_cost_array(self):
        cutoff = self.training_params['cutoff_dim']
        cost_array = np.zeros([cutoff] * self.n_qumodes)
        for indices in np.ndindex(cost_array.shape):
            cost_array[indices] = self.calculate_cost_once(np.clip(indices,0,1))
        return cost_array