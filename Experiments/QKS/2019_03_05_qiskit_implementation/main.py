import numpy as np
from sklearn.linear_model import LogisticRegression
from qiskit import IBMQ
import matplotlib.pyplot as plt

from qks import QuantumKitchenSinks
from make_frames import make_frames


def logistic_regression(X_train, X_test, y_train, y_test):
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


def run_qks(p, number_of_qubits, qc, n_episodes, scale, n_trials):
    """
    Parameters:
    p : int, default = None
        dimension of input vector, inferred from dataset
    qc : object, default = None
        the quantum computer object
    n_episodes : int, default = 1
        number of episodes the dataset is iterated over;
        (i.e. for each sampe in the dataset, we apply the QKS transformation n_episodes number of times)
    scale : int, default = 1
        standard deviation (spread) of the normal distribution
    n_trials : int, default 1000
        the number of times we run the quantujm circuit

    r : int, default = 1
        number of elements that are non-zero s.t. r <= p (dimension of input vector)

    References:
        Quantum Kitchen Sinks was introduced in:
        C. M. Wilson, J. S. Otterbach, N. Tezak, R. S. Smith,
        G. E. Crooks, and M. P. da Silva 2018. Quantum Kitchen
        Sinks. An algorithm for machine learning on near-term
        quantum computers. <https://arxiv.org/pdf/1806.08321.pdf>
    """

    r = 1 if p / number_of_qubits < 1 else int(p / number_of_qubits)
    QKS = QuantumKitchenSinks(qc, n_episodes=n_episodes,
                              r=r, scale=scale,
                              distribution='normal',
                              n_trials=n_trials)
    return QKS


def make_plot(data, target, name, title):
    plt.figure(figsize=(5, 5))
    plt.title(title)
    plt.scatter(data[:0], data[:1], s=5, c=target)
    plt.savefig(name)

    qc = make_qc(q, noisy)
    p = X_train.shape[-1]

    QKS = run_qks(p, 2, qc, 1000, 1, 1000)

    QKS_train = QKS.fit_transform(X_train)
    QKS_test = QKS.fit_transform(X_test)

    train_preds, test_preds = logistic_regression(QKS_train, QKS_test, y_train, y_test)

    plot = True
    img_path = 'figs/'

    if plot is True:
        make_plot(X_train, y_train, img_path + 'training_dataset', 'Training Set')
        make_plot(X_test, y_test, img_path + 'test_dataset', 'Test Set')
        make_plot(X_train, train_preds, img_path + 'results_experiment_train', 'Experiment Results - Training Dataset')
        make_plot(X_test, test_preds, img_path + 'results_experiment_test', 'Experiment Results - Test Dataset')


def main():
    X_train, X_test, y_train, y_test = make_frames(
        train_size=200, test_size=50, outer_length=2, inner_length=1
    )

    n_episodes = 20
    scale = 1
    n_trials = 1000
    number_of_qubits = 2
    noisy = False
    qc = make_qc(q, noisy)

    run_qks(p, number_of_qubits, qc, n_episodes, scale, n_trials)

# Write the API token to IBM Q
my_api_token = ""
IBMQ.save_account(my_api_token)
IBMQ.load_accounts()

# Check the connection for IBM Q
try:
    IBMQ.load_accounts()
except:
    print("""WARNING: There's no connection with the API for remote backends.
             Have you initialized a file with your personal token?
             For now, there's only access to local simulator backends...""")

if __name__ == "__main__":
    np.random.seed(1337)
    main()
