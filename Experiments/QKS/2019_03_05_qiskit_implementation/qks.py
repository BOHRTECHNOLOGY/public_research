# Quantum Kitchen Sinks
import qiskit
import numpy as np

class QuantumKitchenSinks():
    """
    QKS
    
    Parameters:
    qc : object, default = None
        the quantum computer object
    n_episodes : int, default = 1
        number of episodes the dataset is iterated over;
        (i.e. for each sampe in the dataset, we apply the QKS transformation n_episodes number of times)
    p : int, default = None
        dimension of input vector, inferred from dataset
    q : int, default = None
        number of qubits to use
    r : int, default = 1
        number of elements that are non-zero s.t. r <= p (dimension of input vector)
    scale : int, default = 1
        standard deviation (spread) of the normal distribution
    distribution : string, default = 'normal'
        distribution used to create nonzero elements of omega
    n_trials : int, default 1000
        the number of times we run the quantujm circuit
        
    References:
        Quantum Kitchen Sinks was introduced in:
        C. M. Wilson, J. S. Otterbach, N. Tezak, R. S. Smith,
        G. E. Crooks, and M. P. da Silva 2018. Quantum Kitchen
        Sinks. An algorithm for machine learning on near-term
        quantum computers. <https://arxiv.org/pdf/1806.08321.pdf>
    """

    def __init__(self, qc=None, n_episodes=1, p=None, q=None, r=1,
                 scale=1, distribution='normal', n_trials=1000):
        self.qc = qc
        self.n_episodes = n_episodes
        self.p = p
        self.q = q or len(self.qc.qubits())
        self.r = r
        self.scale = scale
        self.distribution = distribution
        self.n_trials = n_trials
        self.num_cols = self.n_episodes*self.q
        self.executable = self._build_and_compile()


    def fit(self, X):
        """Generate set of random parameters for X

        Parameters
        ---------
        X : array, shape (n_samples, n_features)
            Training data
        """

        self.shape = X.shape
        self.p = self.shape[-1]

        if not hasattr(self, 'omega'):
            self.omega = self._make_omega()
            self.beta = self._make_beta()

        self.theta = self._get_theta(X)

    def transform(self):
        """Apply the QKS transformation to the random parameters"""

    def fit_transform(self, X):
        """Generate set of random parameters for X and apply the QKS transformation
        Parameters
        ---------
        X : array, shape (n_samples, n_features)
            Training data
        """

        self.fit(X)
        return self.transform()

    def _make_omega(self):
        """A (q x p) dimensional matrix that is used to encode the input vector into q gate parameters."""

        def _create_selection_matrix():
            """Generates a matrix of 0s and 1s to zero out `r` values per matrix"""

            matrix_size = self.p * self.q
            m = np.zeros(matrix_size)
            for i in range(self.r):
                m[i] = 1
            np.random.shuffle(m)
            selection_matrix = m.reshape(self.q, self.p)
            return selection_matrix

        size = (self.n_episodes, self.q, self.p)

        if self.distribution == "normal":
            dist = np.random.normal(loc=0, scale=self.scale, size=size)
        else:
            raise AttributeError(
                "QKS currently only implemented for normal distributions. Use distribution = 'normal'.")

        selection_matrix = np.array([_create_selection_matrix() for x in range(self.n_episodes)])
        omega = dist * selection_matrix  # matrix chooses which values to keep

        return omega

    def _make_beta(self):
        """random q-dimensional bias vector"""
        return np.random.uniform(low=0, high=(2 * np.pi), size=(self.n_episodes, self.q))

    def _get_theta(self, u):
        """A linear transformation to get our set of random parameters to feed into the quantum circuit
        The code is written in such a way to maintain the same notation used in the paper.
        u: p-dimensional input vector from the dataset
        """
        thetas = []
        for i in range(u.shape[0]):
            for e in range(self.n_episodes):
                thetas.append(self.omega[e].dot(u[i].T) + self.beta[e])

        return np.array(thetas)

    def _build_and_compile(self):
        """ Creates the quantum circuit and compiles the program into an executable. """

        def _ansatz():
            """Mimics the circuits from the appendix of the paper, with the exception of
            the ordering of the circuit.cx gates (before and after compilation they still do not match).
            This is probably best just left up to the compiler.
            For ease of reading the printed operations, the qubits are looped over several times.
            """
            program = qiskit.QuantumProgram()
            qubits = self.qc.qubits()
            n_qubits = self.q
            var = 'theta'

            ro = program.declare('ro', memory_type='BIT', memory_size=n_qubits)
            thetas = {var + str(qubit): program.declare(var + str(qubit), memory_type = 'REAL') for qubit in qubits}

            sq = int(np.sqrt(n_qubits))
            lim = n_qubits - sq - 1

            for m in qubits:
                program += qiskit.rx(thetas[var + str(m)], m)

            for m in qubits:
                m_1 = m + 1
                m_sq = m + sq
                skip = (m_1) % sq

                if m_1 < n_qubits:
                    if (m_sq >= n_qubits): program += qiskit.circuit.cx(m, m_1)
                    else: program += qiskit.circuit.cx(m, m_sq)

                if (m < lim) and (skip != 0): program += qiskit.circuit.cx(m, m_1)

            for m in qubits:
                program += qiskit.measure(m, ro[m])

            print("program instructions from Qiskit:\n")
            for instruction in program.instructions:
                print(instruction)

            return program

        program = _ansatz()
        program.wrap_in_numshots_loop(shots=self.n_trials)
        executable = self.qc.compile(program)
        return executable

    def _qks_run(self, theta):
        # Runs the QKS transformation through the quantum circuit and returns the average measurements
        theta_map = {'theta%s' % pos: [theta[pos]] for pos in range(len(theta))}
        bitstrings = self.qc.run(self.executable, memory_map=theta_map)
        avg_measurements = bitstrings.mean(axis=0)
        return avg_measurements
 
 
