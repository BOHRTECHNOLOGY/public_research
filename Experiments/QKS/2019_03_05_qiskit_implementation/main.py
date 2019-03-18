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

def make_plot(data, target, name, title):
    plt.figure(figsize=(5, 5))
    plt.title(title)
    plt.scatter(data[:0], data[:1], s=5, c=target)
    plt.savefig(name)

    qc = make_qc(q, noisy)
    p = X_train.shape[-1]

    r = 1 if p / q < 1 else int(p / q)

    QKS = QuantumKitchenSinks(qc, n_episodes=n_episodes, r=r, scale=scale, distribution='normal', n_trials=1000)

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
    q = 2
    noisy = False


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
