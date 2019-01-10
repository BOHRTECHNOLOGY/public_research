## Introduction 
`qks.py` contains the initial code to replicate **Quantum Kitchen Sinks** **(An algorithm for machine learning on near-term quantum computers)** by *Christopher M. Wilson, Johannes S. Otterbach, Nikolas Tezak, Robert S. Smith, Gavin E. Crooks, Marcus P. da Silva*. 

- [arxiv paper](https://arxiv.org/pdf/1806.08321.pdf)

- [medium article](https://medium.com/rigetti/quantum-kitchen-sinks-an-algorithm-for-machine-learning-on-near-term-quantum-computers-d26bd776c338)

## Data
The synthetic "picture frames" dataset proposed in the paper was generated via the `make_frames` function. This creates a smaller inner square with sides of length 2 and a larger outer square with sides of length 4. Both have points uniformly distributed around the average. The training set is composed of 1600 two-dimensional points, 800 for each class. While the test set is 400 two-dimensional points, 200 for each class. 


picture frames             |  picture frames
:-------------------------:|:-------------------------:
![training set](https://github.com/zackgow/public_research/raw/quantum_kitchen_sinks/Experiments/forest_QKS/figs/training_dataset.png) |  ![test set](https://github.com/zackgow/public_research/raw/quantum_kitchen_sinks/Experiments/forest_QKS/figs/test_dataset.png)

## Results
Using the parameters below, we were able to achieve an accuracy of **99.5%** on the training set and **99.75%** on the test set using logistic regression after obtaining the feature vector from the Quantum Kitchen Sinks method. 

    Parameters
    ----------
    np.random.seed(1337)

    n_episodes = 20    # number of episodes the dataset is iterated over
    sigma2 = 1         # spread of the distribution.
    n_trials = 1000    # number of shots
    noisy = False      # use pre-configured noise model
    q = 2              # number of qubits to use
    plot = True        # plot graph of the classified datasets
    train_size = 200   # 200 is default to get the size of the dataset in the paper
    test_size = 50     # 50 is default to get the size of the dataset in the paper
     
    Accuracy
    --------
    training set:  99.5%
    test set:      99.75%

picture frames             |  picture frames
:-------------------------:|:-------------------------:
![experiment on training set](https://github.com/zackgow/public_research/raw/quantum_kitchen_sinks/Experiments/forest_QKS/figs/results_experiment_train.png)|  ![experiment on test set](https://github.com/zackgow/public_research/raw/quantum_kitchen_sinks/Experiments/forest_QKS/figs/results_experiment_test.png)


## Conclusion
This is a proof of concept to show that we could replicate the results of the paper. We were able to successfully implement QKS on the synthetic picture frames dataset and achieved over 99% accuracy on our test set. 
