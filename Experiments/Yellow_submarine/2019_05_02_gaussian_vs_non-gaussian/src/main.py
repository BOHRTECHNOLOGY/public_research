from yellow_submarine.maxcut_solver_tf import MaxCutSolver, ParametrizedGate
from strawberryfields.ops import *
import tensorflow as tf
from scipy.stats import rv_discrete
import pdb
from collections import Counter
import sys

adjacency_matrices = {
    'u4' : np.array([
        [ 0,  1,  1,  0],
        [ 1,  0,  1,  1],
        [ 1,  1,  0,  1],
        [ 0,  1,  1,  0],
    ]) / 4,

    'u5' : np.array([
        [ 0,  1,  1,  1,  0],
        [ 1,  0,  1,  1,  1],
        [ 1,  1,  0,  1,  1],
        [ 1,  1,  1,  0,  1],
        [ 0,  1,  1,  1,  0],
    ]) / 8,

    'u6' : np.array([
        [ 0,  1,  1,  1,  1,  0],
        [ 1,  0,  1,  1,  1,  1],
        [ 1,  1,  0,  1,  1,  1],
        [ 1,  1,  1,  0,  1,  1],
        [ 1,  1,  1,  1,  0,  1],
        [ 0,  1,  1,  1,  1,  1],
    ]) / 10,

    'w4' : np.array([
        [  0,  2,  7,  0],
        [  2,  0,  8,  2],
        [  7,  8,  0,  1],
        [  0,  2,  1,  0],
    ]) / 24,

    'w5' : np.array([
        [  0,  2,  7,  9,  0],
        [  2,  0,  8,  4,  5],
        [  7,  8,  0,  1,  6],
        [  9,  4,  1,  0,  3],
        [  0,  5,  6,  3,  0],
    ]) / 40,

    'w6' : np.array([
        [  0,  2,  7,  9, 11,  0],
        [  2,  0,  8,  4,  5, 12],
        [  7,  8,  0,  1,  6, 17],
        [  9,  4,  1,  0,  3, 14],
        [ 11,  5,  6,  3,  0, 15],
        [  0, 12, 17, 14, 15,  0],
    ]) / 82,
}

interferometer_matrices = {
    'i4' : np.array([
        [-0.16572193-0.46458312j,  0.0790278 -0.51989778j, -0.49901635-0.08823656j,  0.37266057+0.29065573j],
        [ 0.33280397+0.08022457j, -0.4550813 -0.57248497j,  0.48890504-0.29523262j,  0.14620994-0.01999298j],
        [ 0.25623693-0.02851655j, -0.31491964-0.25811727j, -0.32743693+0.36369309j, -0.70501687+0.17661863j],
        [ 0.1995225 -0.73022223j,  0.15013099-0.01687164j,  0.28647722+0.30894943j, -0.05107711-0.47330168j],
    ]),

    'i5' : np.array([
        [ 0.16306234+0.05530423j, -0.22650238+0.32291605j, -0.06453228-0.75504333j, -0.44850712+0.08189646j, -0.09510122+0.15365302j],
        [-0.36026784-0.15296578j,  0.06818781-0.7028499j , -0.01807924-0.43295787j,  0.1796326 +0.28639821j, -0.09711798+0.19146256j],
        [-0.56550193+0.64263291j,  0.2088756 +0.09750988j,  0.07536134+0.12895381j, -0.35173467+0.25417165j,  0.05786428+0.01077566j],
        [-0.03713355+0.04273234j, -0.06041434+0.25926787j,  0.09998542+0.18354685j,  0.25734226+0.11029682j, -0.63385301+0.63409678j],
        [-0.28403786+0.02255455j,  0.11283284+0.45720475j,  0.19942437-0.36359421j,  0.63894238+0.053705j  ,  0.0564052 -0.33280983j],
    ]),

    'i6' : np.array([
        [ 0.46790958-0.12864953j,  0.12236061-0.18019917j, -0.19761074+0.22197692j, -0.15109985+0.61038185j, -0.32088738-0.11548043j, -0.34204939+0.00655085j],
        [-0.09361981-0.15935595j,  0.36557239+0.06475699j, -0.38456451+0.1495774j ,  0.15705213-0.27232777j,  0.41144942-0.17738023j, -0.52829415+0.28118366j],
        [-0.52506686+0.23612392j, -0.26449537+0.27800373j, -0.39975757+0.05467929j, -0.24796446+0.28646886j, -0.15783975+0.30161277j, -0.10908245+0.29525763j],
        [-0.54547732+0.06487601j,  0.12437437+0.02928752j,  0.31311741-0.00863067j,  0.19360214+0.44105686j,  0.09096344-0.48627227j, -0.15319057-0.28911329j],
        [-0.11631712+0.11473207j, -0.28077623-0.4660686j , -0.51209186+0.34705317j,  0.25945463-0.08786254j,  0.05225809-0.04278326j,  0.14950796-0.43888176j],
        [-0.02977815+0.2637555j , -0.07550802-0.59109406j,  0.2858571 -0.12689283j, -0.19610128+0.12930224j,  0.42921529+0.36542495j, -0.31004366+0.08702618j],
    ])
}

adjacency_interferometer_matrices = {
    'u4' : 'i4',
    'u5' : 'i5',
    'u6' : 'i6',
    'w4' : 'i4',
    'w5' : 'i5',
    'w6' : 'i6',
}

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

def assess_cost_based_on_output(outputs, adjacency_matrix):
    cost = 0
    for encoding in outputs:
        cost += calculate_cost_for_encoding(adjacency_matrix, encoding) 
    return cost / len(outputs)

def calculate_cost_for_encoding(adjacency_matrix, encoding):
    cost_value = 0
    for i in range(len(encoding)):
        for j in range(len(encoding)):
            cost_value += 0.5 * adjacency_matrix[i][j] * (encoding[i] - encoding[j])**2
    return cost_value


def run_single_test(learner_params, training_params, matrices, gates_structure):
    log = {'Trace': 'trace'}
    max_cut_solver = MaxCutSolver(learner_params, training_params, matrices, gates_structure, log=log)

    final_cost, all_probs = max_cut_solver.train_and_evaluate_circuit(verbose=False)
    return final_cost, all_probs


def main(matrix, run_id = 0, use_s = 1, use_d = 1, use_ng = 1):
    adjacency_matrix = adjacency_matrices[matrix]

    interferometer_matrix = interferometer_matrices[adjacency_interferometer_matrices[matrix]]

    matrices = [adjacency_matrix, interferometer_matrix]

    # Learner parameters
    learner_params = {
        'task': 'optimization',
        'regularization_strength': 1e-3,
        'optimizer': 'SGD',
        'init_learning_rate': 0.25,
        'log_every': 1,
        'print_log': False
    }

    # Training parameters
    var_cutoff_dim = 17
    if matrix == "u5" or matrix == "w5":
        var_cutoff_dim = 12
    elif matrix == "u6" or matrix == "w6":
        var_cutoff_dim = 9

    training_params = {
        'steps': 400,
        'cutoff_dim': var_cutoff_dim
    }

    # Gate structures
    gates_structure = []

    # Squeeze gates structure
    if use_s==1:
        gates_structure.append([
            Sgate,
            0,
            {"constant": np.random.random() - 0.5, "name": 's_magnitude_0', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 's_phase_0', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Sgate,
            1,
            {"constant": np.random.random() - 0.5, "name": 's_magnitude_1', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 's_phase_1', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Sgate,
            2,
            {"constant": np.random.random() - 0.5, "name": 's_magnitude_2', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 's_phase_2', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Sgate,
            3,
            {"constant": np.random.random() - 0.5, "name": 's_magnitude_3', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 's_phase_3', 'regularize': True, 'monitor': True}
        ])
        if matrix == "u5" or matrix == "w5":
            gates_structure.append([
                Sgate,
                4,
                {"constant": np.random.random() - 0.5, "name": 's_magnitude_4', 'regularize': True, 'monitor': True},
                {"constant": np.random.random()*2*np.pi, "name": 's_phase_4', 'regularize': True, 'monitor': True}
            ])
        if matrix == "u6" or matrix == "w6":
            gates_structure.append([
                Sgate,
                5,
                {"constant": np.random.random() - 0.5, "name": 's_magnitude_5', 'regularize': True, 'monitor': True},
                {"constant": np.random.random()*2*np.pi, "name": 's_phase_5', 'regularize': True, 'monitor': True}
            ])

    # Displacement gates structure
    if use_d==1:
        gates_structure.append([
            Dgate,
            0,
            {"constant": np.random.random() - 0.5, "name": 'd_magnitude_0', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 'd_phase_0', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Dgate,
            1,
            {"constant": np.random.random() - 0.5, "name": 'd_magnitude_1', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 'd_phase_1', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Dgate,
            2,
            {"constant": np.random.random() - 0.5, "name": 'd_magnitude_2', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 'd_phase_2', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Dgate,
            3,
            {"constant": np.random.random() - 0.5, "name": 'd_magnitude_3', 'regularize': True, 'monitor': True},
            {"constant": np.random.random()*2*np.pi, "name": 'd_phase_3', 'regularize': True, 'monitor': True}
        ])
        if matrix == "u5" or matrix == "w5":
            gates_structure.append([
                Dgate,
                4,
                {"constant": np.random.random() - 0.5, "name": 'd_magnitude_4', 'regularize': True, 'monitor': True},
                {"constant": np.random.random()*2*np.pi, "name": 'd_phase_4', 'regularize': True, 'monitor': True}
            ])
        if matrix == "u6" or matrix == "w6":
            gates_structure.append([
                Dgate,
                5,
                {"constant": np.random.random() - 0.5, "name": 'd_magnitude_5', 'regularize': True, 'monitor': True},
                {"constant": np.random.random()*2*np.pi, "name": 'd_phase_5', 'regularize': True, 'monitor': True}
            ])
    
    # Kerr gate structure
    if use_ng==1:
        gates_structure.append([
            Kgate,
            0,
            {"constant": np.random.random() - 0.5, "name": 'kerr_0', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Kgate,
            1,
            {"constant": np.random.random() - 0.5, "name": 'kerr_1', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Kgate,
            2,
            {"constant": np.random.random() - 0.5, "name": 'kerr_2', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Kgate,
            3,
            {"constant": np.random.random() - 0.5, "name": 'kerr_3', 'regularize': True, 'monitor': True}
        ])
        if matrix == "u5" or matrix == "w5":
            gates_structure.append([
                Kgate,
                4,
                {"constant": np.random.random() - 0.5, "name": 'kerr_4', 'regularize': True, 'monitor': True}
            ])
        if matrix == "u6" or matrix == "w6":
            gates_structure.append([
                Kgate,
                5,
                {"constant": np.random.random() - 0.5, "name": 'kerr_5', 'regularize': True, 'monitor': True}
            ])

    # Cubic gate structure
    elif use_ng==2:
        gates_structure.append([
            Vgate,
            0,
            {"constant": np.random.random() - 0.5, "name": 'cubic_0', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Vgate,
            1,
            {"constant": np.random.random() - 0.5, "name": 'cubic_1', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Vgate,
            2,
            {"constant": np.random.random() - 0.5, "name": 'cubic_2', 'regularize': True, 'monitor': True}
        ])
        gates_structure.append([
            Vgate,
            3,
            {"constant": np.random.random() - 0.5, "name": 'cubic_3', 'regularize': True, 'monitor': True}
        ])
        if matrix == "u5" or matrix == "w5":
            gates_structure.append([
                Vgate,
                4,
                {"constant": np.random.random() - 0.5, "name": 'cubic_4', 'regularize': True, 'monitor': True}
            ])
        if matrix == "u6" or matrix == "w6":
            gates_structure.append([
                Vgate,
                5,
                {"constant": np.random.random() - 0.5, "name": 'cubic_5', 'regularize': True, 'monitor': True}
            ])

    print("Starting", use_s, use_d, use_ng, run_id)
    model_dir = "logsAuto2_s_{0}_d_{1}_ng_{2}_run_{3}".format(use_s, use_d, use_ng, run_id)
    training_params['model_dir'] = model_dir
    cost, all_probs = run_single_test(learner_params, training_params, matrices, gates_structure)
    total_prob = np.sum(all_probs)
    all_probs = all_probs / total_prob
    cutoff_dim = training_params['cutoff_dim']
    values_flat = [list_to_number(i, cutoff_dim) for i in np.ndindex(all_probs.shape)]
    indices_array = np.reshape(values_flat, all_probs.shape)
    final_distribution = rv_discrete(values=(indices_array, all_probs))
    circuit_outputs_raw = final_distribution.rvs(size=1000)
    circuit_outputs_num = [number_to_base(i, cutoff_dim, len(adjacency_matrix)) for i in circuit_outputs_raw]
    circuit_outputs_clipped = [np.clip(i, 0, 1) for i in circuit_outputs_num]
    circuit_outputs_str = [str(i) for i in circuit_outputs_clipped]
    output_counter = Counter(circuit_outputs_str)
    print("cost:", cost)
    print("total prob:", total_prob)
    for el in output_counter.most_common()[:10]:
        print(el)

    output_cost = assess_cost_based_on_output(circuit_outputs_clipped, adjacency_matrix)
    print("cost from output:", output_cost)

    cost_tensor = tf.convert_to_tensor(cost);
    total_prob_tensor = tf.convert_to_tensor(total_prob)
    output_cost_tensor = tf.convert_to_tensor(output_cost);

    cost_summary = tf.summary.scalar(name = 'cost', tensor = cost_tensor)
    total_prob_summary = tf.summary.scalar(name = 'total_prob', tensor = total_prob_tensor)
    output_cost_summary = tf.summary.scalar(name = 'output_cost', tensor = output_cost_tensor)

    init = tf.global_variables_initializer()

    with tf.Session() as sess:
        writer = tf.summary.FileWriter(model_dir, sess.graph)
        sess.run(init)
        
        cost_value = sess.run(cost_summary)
        writer.add_summary(cost_value)
        
        total_prob_value = sess.run(total_prob_summary)
        writer.add_summary(total_prob_value)

        output_cost_value = sess.run(output_cost_summary)
        writer.add_summary(output_cost_value)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
