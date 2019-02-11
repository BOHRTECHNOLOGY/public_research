# Yellow Submarine - reproducibility, correct version

## Overview

The main goal of this research was to check how similar are consecutive runs of Yellow Submarine - a MaxCut solver. The output of the algorithm is probabilistic, since the parameters are randomly initialized - this might cause the algorithm to converge into very different solutions with every run and hence a huge number of repetitions might be required to achieve a confidence that the results we get are reproducible.

This was also an opportunity to do some initial tests on what are the reasonable values of the algorithm parameters.

## Code 

The main `yellow_submarine` engine comes from https://github.com/BOHRTECHNOLOGY/yellow_submarine, commit hash: `e4d4c16454af4d60843333f3cba8f7e98fa83381`.

The following versions of the libraries has been used:
- qmlt==0.7.1
- StrawberryFields==0.9.0

### Tensorflow problems

Due to some problems with resetting values of tensors in tensorflow, in order to run several consecutive runs, you need to use `runner.py` script instead of `main.py`.

## Description

We have checked how the algorithm behaves between different runs for the same set of parameters.
We have used the following parameters:
```
    matrix_divisor = 3
    A = np.array([[c, 1, 1, 0],
        [1, c, 1, 1],
        [1, 1, c, 1],
        [0, 1, 1, c]])
    A = A / matrix_divisor

    interferometer_matrix = \
        np.array(
            [[1, -1, 1, -1],
            [1, 1, 1, 1],
            [-1, -1, 1, 1],
            [1, -1, -1, 1]
            ]) / 2

    learner_params = {
        'task': 'optimization',
        'regularization_strength': 2e-5,
        'optimizer': 'SGD',
        'init_learning_rate': 0.1,
        'log_every': 1,
        'print_log': False
        }

    training_params = {
        'steps': 200,
        'cutoff_dim': 17
        }
```

### Cost function

Two following method of evaluating cost have been used. Method A:

1. Calculate the costs of all possible states
2. Take the probability of all possible states
3. Perform element-wise multiplication of these two arrays
4. Sum over all elements
5. Divide by the sum of all probabilities (normalization)

This method corresponds to encoding where 0 in resulting state corresponds to 0 in a solution, and all other numbers to 1.


## Results 

Unfortunately the files generated during the training process are too big to store them in the repository and we have not found a way to export the results from Tensorboard without a huge manual overhead.


### Observation 1

The results for given set of parameters were very similar - there were some differences in the final result, however they were rather minor. Also, evolution of the parameters was smooth, without any major changes between runs.
Though it is worth noting, that the final value of the cost function differed between runs - i.e. it has not always converged to the same value.

### Observation 2
The training process is very smooth - this is probably due to the methods of cost function used.

Even though these methods works very well, they are not very practical for larger problems and outside of the simulator. There are, however, a couple of reasons for using it in this setup:
- it is an exploratory study.
- if the algorithm will fail with the most accurate value of the loss function, it will probably fail for the less accurate too. If it works, then we experiment with different loss functions.
- in practical setting we would have a set of measurements, which gives us an approximation of the tensor of probabilities of all the states. The more measurements we have, the better approximation we get. Also, we don't need to calculate the costs of all the possible solutions - we only need to evaluate those that we have sampled.

### Observation 3
400 steps was not enough to converge for most cases.


### Observation 4
Most tests were performed with the `learning_rate=0.1`. However, when it was increased to `1.0`, the training process was much less smooth and the characteristic oscillations appeared for almost all the parameters.

### Observation 5
Parameters of the Kerr gates were almost always changing extremely slow - at the rate of 0.1 across whole training or slower. This suggests, that these gates don't have much influence on the final result.

### Observation 6
The value of trace was changing throughout the training. It can usually be kept above level of 0.9 with enough regularisation and high enough cutoff value.

### Observation 7

The resulting circuit is always able to find only one (out of two) solutions - in case of the matrix we used it was either [0,1,1,0] or [1,0,0,1].


## Conclusions

Based on the results we decided to make the following decisions:
- the following parameters need to be optimized: `init_learning_rate`, `regularization_strength`.
- remove normalization step from the cost function and we will use method A.
- 10 repetitions of training process seems to be enough to get a representative sample.
- 400 steps seems not to be enough iterations for the algorithm to converge. It might mean, that the higher learning rate is needed for faster convergence.
