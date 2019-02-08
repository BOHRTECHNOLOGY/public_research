from yellow_submarine.maxcut_solver_ml import MaxCutSolver, ParametrizedGate
from yellow_submarine.maxcut_solver_ml import assess_all_solutions_clasically
from strawberryfields.ops import *
from scipy.stats import rv_discrete
import pdb
from collections import Counter
import sys

def number_to_base(n, b, length):
    # Source: https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-in-any-base-to-a-string
    digits = [0] * length
    if n == 0:
        return digits
    i = 0
    while n:
        digits[i] = int(n % b)
        i += 1
        n //= b
    return digits[::-1]

def list_to_number(l, b):
    number = 0
    for power, el in enumerate(l[::-1]):
        number += el*b**power
    return number

def assess_cost_based_on_output(outputs, A):
    cost = 0
    for encoding in outputs:
        cost += calculate_cost_for_encoding(A, encoding) 
    return cost / len(outputs)

def calculate_cost_for_encoding(A, encoding):
    cost_value = 0
    for i in range(len(encoding)):
        for j in range(len(encoding)):
            cost_value += 0.5 * A[i][j] * (encoding[i] - encoding[j])**2
    return cost_value


def run_single_test(learner_params, training_params, adj_matrices, gates_structure):
    log = {'Trace': 'trace'}
    max_cut_solver = MaxCutSolver(learner_params, training_params, adj_matrices, gates_structure, log=log)

    final_costs, all_probs_list = max_cut_solver.train_and_evaluate_circuit(verbose=False)

    return final_costs, all_probs_list


def main(run_id=0, use_ng=1):
    c = 3
    # Initial set of matrices used for training
    # A_0 = np.array([[c, 1, 1, 1],
    #     [1, c, 1, 1],
    #     [1, 1, c, 1],
    #     [1, 1, 1, c]])

    # A_1 = np.array([[c, 1, 1, 0],
    #     [1, c, 1, 1],
    #     [1, 1, c, 1],
    #     [0, 1, 1, c]])

    # A_2 = np.array([[c, 0, 1, 0],
    #     [0, c, 1, 1],
    #     [1, 1, c, 1],
    #     [0, 1, 1, c]])

    # A_3 = np.array([[c, 1, 0, 0],
    #     [1, c, 1, 0],
    #     [0, 1, c, 1],
    #     [0, 0, 1, c]])

    A_0 = np.array([[c, 1, 1, 1],
        [1, c, 0, 0],
        [1, 0, c, 0],
        [1, 0, 0, c]])

    A_1 = np.array([[c, 1, 0, 0],
        [1, c, 1, 1],
        [0, 1, c, 0],
        [0, 1, 0, c]])

    A_2 = np.array([[c, 0, 1, 0],
        [0, c, 1, 0],
        [1, 1, c, 1],
        [0, 0, 1, c]])

    A_3 = np.array([[c, 0, 0, 1],
        [0, c, 0, 1],
        [0, 0, c, 1],
        [1, 1, 1, c]])



    adj_matrices = [A_0, A_1, A_2, A_3]

    learner_params = {
        'task': 'optimization',
        'regularization_strength': 1e-4,
        'optimizer': 'SGD',
        'init_learning_rate': 0.1,
        'log_every': 1,
        'print_log': False
        }

    training_params = {
        'steps': 400,
        'cutoff_dim': 17
        }

    gates_structure = []
    gates_structure.append([Sgate, 0, {"constant": np.random.random() - 0.5, "name": 's_magnitude_00', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_00', 'regularize': True, 'monitor': False}])
    gates_structure.append([Sgate, 1, {"constant": np.random.random() - 0.5, "name": 's_magnitude_01', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_01', 'regularize': True, 'monitor': False}])
    gates_structure.append([Sgate, 2, {"constant": np.random.random() - 0.5, "name": 's_magnitude_02', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_02', 'regularize': True, 'monitor': False}])
    gates_structure.append([Sgate, 3, {"constant": np.random.random() - 0.5, "name": 's_magnitude_03', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_03', 'regularize': True, 'monitor': False}])
    
    gates_structure.append([Sgate, 0, {"constant": np.random.random() - 0.5, "name": 's_magnitude_10', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_10', 'regularize': True, 'monitor': False}])
    gates_structure.append([Sgate, 1, {"constant": np.random.random() - 0.5, "name": 's_magnitude_11', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_11', 'regularize': True, 'monitor': False}])
    gates_structure.append([Sgate, 2, {"constant": np.random.random() - 0.5, "name": 's_magnitude_12', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_12', 'regularize': True, 'monitor': False}])
    gates_structure.append([Sgate, 3, {"constant": np.random.random() - 0.5, "name": 's_magnitude_13', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 's_phase_13', 'regularize': True, 'monitor': False}])

    gates_structure.append([Dgate, 0, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_00', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_00', 'regularize': True, 'monitor': False}])
    gates_structure.append([Dgate, 1, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_01', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_01', 'regularize': True, 'monitor': False}])
    gates_structure.append([Dgate, 2, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_02', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_02', 'regularize': True, 'monitor': False}])
    gates_structure.append([Dgate, 3, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_03', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_03', 'regularize': True, 'monitor': False}])
    
    gates_structure.append([Dgate, 0, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_10', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_10', 'regularize': True, 'monitor': False}])
    gates_structure.append([Dgate, 1, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_11', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_11', 'regularize': True, 'monitor': False}])
    gates_structure.append([Dgate, 2, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_12', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_12', 'regularize': True, 'monitor': False}])
    gates_structure.append([Dgate, 3, {"constant": np.random.random() - 0.5, "name": 'd_magnitude_13', 'regularize': True, 'monitor': False},
        {"constant": np.random.random()*2*np.pi, "name": 'd_phase_13', 'regularize': True, 'monitor': False}])

    if use_ng == 1:
        gates_structure.append([Kgate, 0, {"constant": np.random.random() - 0.5, "name": 'kerr_00', 'regularize': True, 'monitor': True}])
        gates_structure.append([Kgate, 1, {"constant": np.random.random() - 0.5, "name": 'kerr_01', 'regularize': True, 'monitor': True}])
        gates_structure.append([Kgate, 2, {"constant": np.random.random() - 0.5, "name": 'kerr_02', 'regularize': True, 'monitor': True}])
        gates_structure.append([Kgate, 3, {"constant": np.random.random() - 0.5, "name": 'kerr_03', 'regularize': True, 'monitor': True}])
        gates_structure.append([Kgate, 0, {"constant": np.random.random() - 0.5, "name": 'kerr_10', 'regularize': True, 'monitor': True}])
        gates_structure.append([Kgate, 1, {"constant": np.random.random() - 0.5, "name": 'kerr_11', 'regularize': True, 'monitor': True}])
        gates_structure.append([Kgate, 2, {"constant": np.random.random() - 0.5, "name": 'kerr_12', 'regularize': True, 'monitor': True}])
        gates_structure.append([Kgate, 3, {"constant": np.random.random() - 0.5, "name": 'kerr_13', 'regularize': True, 'monitor': True}])

    elif use_ng == 2:
        gates_structure.append([Vgate, 0, {"constant": np.random.random() - 0.5, "name": 'cubic_00', 'regularize': True, 'monitor': True}])
        gates_structure.append([Vgate, 1, {"constant": np.random.random() - 0.5, "name": 'cubic_01', 'regularize': True, 'monitor': True}])
        gates_structure.append([Vgate, 2, {"constant": np.random.random() - 0.5, "name": 'cubic_02', 'regularize': True, 'monitor': True}])
        gates_structure.append([Vgate, 3, {"constant": np.random.random() - 0.5, "name": 'cubic_03', 'regularize': True, 'monitor': True}])
        gates_structure.append([Vgate, 0, {"constant": np.random.random() - 0.5, "name": 'cubic_10', 'regularize': True, 'monitor': True}])
        gates_structure.append([Vgate, 1, {"constant": np.random.random() - 0.5, "name": 'cubic_11', 'regularize': True, 'monitor': True}])
        gates_structure.append([Vgate, 2, {"constant": np.random.random() - 0.5, "name": 'cubic_12', 'regularize': True, 'monitor': True}])
        gates_structure.append([Vgate, 3, {"constant": np.random.random() - 0.5, "name": 'cubic_13', 'regularize': True, 'monitor': True}])


    print("Starting", run_id, 'ng', use_ng)
    model_dir = "logsAuto_run_{0}_ng_{1}".format(run_id, use_ng)
    training_params['model_dir'] = model_dir
    final_costs, all_probs_list = run_single_test(learner_params, training_params, adj_matrices, gates_structure)

    for cost, all_probs, A in zip(final_costs, all_probs_list, adj_matrices):
        total_prob = np.sum(all_probs)
        all_probs = all_probs / total_prob
        cutoff_dim = training_params['cutoff_dim']
        values_flat = [list_to_number(i, cutoff_dim) for i in np.ndindex(all_probs.shape)]
        indices_array = np.reshape(values_flat, all_probs.shape)
        final_distribution = rv_discrete(values=(indices_array, all_probs))
        circuit_outputs_raw = final_distribution.rvs(size=1000)
        circuit_outputs_num = [number_to_base(i, cutoff_dim, len(A)) for i in circuit_outputs_raw]
        circuit_outputs_clipped = [np.clip(i, 0, 1) for i in circuit_outputs_num]
        circuit_outputs_str = [str(i) for i in circuit_outputs_clipped]
        output_counter = Counter(circuit_outputs_str)
        print("cost:", cost)
        print("total prob:", total_prob)
        for el in output_counter.most_common()[:10]:
            encoding = np.fromstring(el[0][1:-1], sep=' ').astype(int)
            print(el, calculate_cost_for_encoding(A, encoding))

        print("cost from output:", assess_cost_based_on_output(circuit_outputs_clipped, A))
    print(assess_all_solutions_clasically(A))

if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]))