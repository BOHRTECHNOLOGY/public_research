from maxcut_solver_tf import MaxCutSolver, ParametrizedGate
from strawberryfields.ops import *


def main():


    c = 3
    A = np.array([[c, 1, 1, 0],
        [1, c, 1, 1],
        [1, 1, c, 1],
        [0, 1, 1, c]])

    # TODO add check for eigenvalues 1 and -1
    print("Eigenvalues: ", np.linalg.eigvals(A))

    interferometer_matrix = \
        np.array(
            [[1, -1, 1, -1],
            [1, 1, 1, 1],
            [-1, -1, 1, 1],
            [1, -1, -1, 1]
            ]) / 2

    matrices = [A, interferometer_matrix]
    learner_params = {
        'task': 'optimization',
        'regularization_strength': 2e-5,
        'optimizer': 'SGD',
        'init_learning_rate': 0.01,
        'log_every': 1
        }

    training_params = {
        'steps': 200,
        'cutoff_dim': 17
        }

    log = {'Trace': 'trace'}

    gates_structure = []

    gates_structure.append([Sgate, 0, {"constant": np.random.random() - 0.5, "name": 'squeeze_0', 'regularize': True, 'monitor': True}])
    gates_structure.append([Sgate, 1, {"constant": np.random.random() - 0.5, "name": 'squeeze_1', 'regularize': True, 'monitor': True}])
    gates_structure.append([Sgate, 2, {"constant": np.random.random() - 0.5, "name": 'squeeze_2', 'regularize': True, 'monitor': True}])
    gates_structure.append([Sgate, 3, {"constant": np.random.random() - 0.5, "name": 'squeeze_3', 'regularize': True, 'monitor': True}])

    gates_structure.append([Dgate, 0, {"constant": np.random.random() - 0.5, "name": 'displacement_0', 'regularize': True, 'monitor': True}])
    gates_structure.append([Dgate, 1, {"constant": np.random.random() - 0.5, "name": 'displacement_1', 'regularize': True, 'monitor': True}])
    gates_structure.append([Dgate, 2, {"constant": np.random.random() - 0.5, "name": 'displacement_2', 'regularize': True, 'monitor': True}])
    gates_structure.append([Dgate, 3, {"constant": np.random.random() - 0.5, "name": 'displacement_3', 'regularize': True, 'monitor': True}])

    gates_structure.append([Kgate, 0, {"constant": np.random.random() - 0.5, "name": 'kerr_0', 'regularize': True, 'monitor': True}])
    gates_structure.append([Kgate, 1, {"constant": np.random.random() - 0.5, "name": 'kerr_1', 'regularize': True, 'monitor': True}])
    gates_structure.append([Kgate, 2, {"constant": np.random.random() - 0.5, "name": 'kerr_2', 'regularize': True, 'monitor': True}])
    gates_structure.append([Kgate, 3, {"constant": np.random.random() - 0.5, "name": 'kerr_3', 'regularize': True, 'monitor': True}])

    max_cut_solver = MaxCutSolver(learner_params, training_params, matrices, gates_structure, log=log)
    max_cut_solver.train_and_evaluate_circuit()
    max_cut_solver.assess_all_solutions_clasically()

if __name__ == '__main__':
    main()