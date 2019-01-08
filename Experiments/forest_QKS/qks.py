import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle

from pyquil import get_qc
from pyquil.quil import Program
from pyquil.gates import RX, CNOT, MEASURE


def make_frames(num):
    """
    The picture frames dataset contains a smaller inner square
    with sides of length 2 and a larger outer square with sides
    of length 4. Both have points uniformally distributed around
    the average.
    """
    def zip_arrays(d1, d2):
        return np.array(list(zip(d1, d2)))

    def make_squares(num, l):
        left_right, top_bottom = make_barriers(num, l), make_barriers(num, l)
        top_bottom[:,[0,1]] = top_bottom[:,[1,0]] 
        square = np.concatenate((left_right, top_bottom))
        return square

    def make_barriers(num, l):
        dist = 0.1 * l
        left = np.random.uniform((-l - dist), (-l + dist), num)
        right = np.random.uniform((l - dist), (l + dist), num)
        left_barrier = np.random.uniform(-l, l, num)
        right_barrier = np.random.uniform(-l, l, num)
        L = zip_arrays(left, left_barrier)
        R = zip_arrays(right, right_barrier)
        barriers = np.vstack((L, R))
        return barriers
    
    outer = make_squares(num, l=2)
    inner = make_squares(num, l=1)
    frames = np.concatenate((outer, inner))
    
    half = int((len(frames) / 2))
    target = np.concatenate((np.zeros(half), np.ones(half)))
    
    X, y = shuffle(frames, target, random_state=1337)
    return X, y


def make_omega(n_episodes, p, q, r, scale, loc=0):
    """
    encodes the input vector into q gate parameters
    """

    def create_selection_matrix(p, q, r):
        """
        Generates a matrix of 0s and 1s to zero out `r` values per matrix
        """
        matrix_size = p * q
        m = np.zeros(matrix_size)
        for i in range(r): m[i] = 1
        np.random.shuffle(m)
        selection_matrix = m.reshape(q, p)
        return selection_matrix

    norm_dist = np.random.normal(loc, scale, size=(n_episodes, q, p))
    selection_matrix = np.array([create_selection_matrix(p, q, r) for x in range(n_episodes)])
    omega = norm_dist * selection_matrix # matrix chooses which values to keep
    return omega


def get_beta(n_episodes, q):
    """
    q-dimensional bias vector
    """
    return np.random.uniform(low=0, high=(2 * np.pi), size=(n_episodes, q))


def get_theta(omega, u, beta, n_episodes):
    """
    random parameters
    """
    theta = [omega[e].dot(u[i].T) + beta[e]
             for i in range(u.shape[0]) 
             for e in range(n_episodes)
             ]
    return np.array(theta)


def make_qc(q, noisy=False):
    q_str = str(q) + 'q'
    qvm = '-qvm'
    name = q_str + qvm if not noisy else q_str + '-noisy' + qvm
    print("name of qc: ", name)
    qc = get_qc(name)
    return qc


def ansatz(qc):
    """
    This function creates the quantum circuit and performs the measurements.
    It mimics the circuits from the appendix of the paper, with the exception of
    the ordering of the CNOT gates (before and after compilation they still do not match).
    This is probably best just left up to the compiler.

    For ease of reading the printed operations, the qubits are looped over several times.
    """    
    program = Program()
    qubits = qc.qubits()
    n_qubits = len(qubits)
    var = 'theta'

    ro = program.declare('ro', memory_type='BIT', memory_size=n_qubits)
    thetas = {var + str(qubit): program.declare(var + str(qubit), memory_type = 'REAL') for qubit in qubits}

    sq = int(np.sqrt(n_qubits))
    lim = n_qubits - sq - 1 
    
    for m in qubits: program += RX(thetas[var + str(m)], m)
    for m in qubits:
        m_1 = m + 1
        m_sq = m + sq
        skip = (m_1) % sq
        
        if m_1 < n_qubits:
            if (m_sq >= n_qubits): program += CNOT(m, m_1)
            else: program += CNOT(m, m_sq)
    
        if (m < lim) and (skip != 0): program += CNOT(m, m_1)

    for m in qubits: program += MEASURE(m, ro[m])

    print("program instructions from pyquil:\n")
    for instruction in program.instructions:
        print(instruction) 

    return program


def qks_run(qc, executable, theta):
    theta_map = {'theta%s'%pos: [theta[pos]] for pos in range(len(theta))}
    bitstrings = qc.run(executable, memory_map=theta_map)
    avg_measurements = bitstrings.mean(axis=0)
    return avg_measurements


def logistic_regression(X_train, y_train, X_test, y_test):
    lr = LogisticRegression(solver='lbfgs')
    lr.fit(X_train, y_train)

    train_acc = lr.score(X_train, y_train)
    test_acc = lr.score(X_test, y_test)

    print(
        "accuracy\n----- \n training: {}\n test:     {}"
          .format(train_acc, test_acc)
         )

    train_preds = lr.predict(X_train)
    test_preds = lr.predict(X_test)

    return train_preds, test_preds


def make_plot(data, target, name, title):
    plt.figure(figsize=(5, 5))
    plt.title(title)
    plt.scatter(data[:,0], data[:,1], s=5, c=target)
    plt.savefig(name)


def main():
    np.random.seed(1337)

    n_episodes = 20    # number of episodes the dataset is iterated over
    sigma2 = 1         # spread of the distribution.
    n_trials = 1000    # number of shots
    noisy = False      # use pre-configured noise model
    q = 2              # number of qubits to use
    plot = True        # plot graph of the classified datasets
    train_size = 200   # 200 is default to get the size of the dataset in the paper
    test_size = 50     # 50 is default to get the size of the dataset in the paper
    
    img_path = 'figs/'
    num_cols = n_episodes * q # number of columns after QKS transformation

    # make picture frames dataset
    train, y_train = make_frames(train_size)
    test, y_test = make_frames(test_size)

    p = train.shape[-1] # dimension of input vector
    r = 1 if p / q < 1 else int(p / q)  # number of elements that are non-zero s.t. r<=p

    beta  = get_beta(n_episodes, q)
    omega = make_omega(n_episodes, p, q, r, sigma2, 0)

    train_theta = get_theta(omega, train, beta, n_episodes)
    test_theta = get_theta(omega, test, beta, n_episodes)

    # make QC, circuits, run and measure
    qc = make_qc(q, noisy)
    program = ansatz(qc)
    program.wrap_in_numshots_loop(shots=n_trials)
    executable = qc.compile(program)

    train_QKS = [qks_run(qc, executable, theta) for theta in train_theta]
    test_QKS = [qks_run(qc, executable, theta) for theta in test_theta]

    # ensure that the shape is correct for regression/classification
    X_train = np.array(train_QKS).reshape(train.shape[0], num_cols)
    X_test = np.array(test_QKS).reshape(test.shape[0], num_cols)

    train_preds, test_preds = logistic_regression(X_train, y_train, X_test, y_test)

    if plot is True:
        make_plot(train, y_train, img_path + 'training_dataset', 'Training Set')
        make_plot(test, y_test, img_path + 'test_dataset', 'Test Set')
        make_plot(train, train_preds, img_path + 'results_experiment_train', 'Experiment Results - Training Dataset')
        make_plot(test, test_preds, img_path + 'results_experiment_test', 'Experiment Results - Test Dataset') 


if __name__ == "__main__":
    main()
