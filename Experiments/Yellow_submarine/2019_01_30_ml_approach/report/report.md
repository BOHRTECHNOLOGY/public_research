# Yellow Submarine - ML approach

## Overview

In this experiment instead of training the circuit to solve a single graph, we took approach more akin to machine learning. TODO

## Code 

The code is built on top of `2019_01_23_investigating_layers`, commit hash: `aad77a501fbea913503edb14063a570e514e72aa`

You can find the versions of the libraries used in this experiment in `requirements.txt` file.

### Tensorflow problems

Due to some problems with resetting values of tensors in tensorflow, in order to run several consecutive runs, you need to use `runner.py` script instead of `main.py`.

## Description

The "machine learning" approach works as follows:

1. We pass several graphs (in the form of adjacency matrix) to the solver as input.
2. During every iteration, for every graph, we build a circuit and evaluate it.
3. The cost for given set parameters is sum of costs of outputs of all the created circuits.


## Results

### Observation 1

For the initial set of matrices some of the matrices had the same solutions. Hence, it was easy for the system to learn to output this solution regardless of the input matrix.
Hence, we have decided to use different set of matrices, where every matrix had different solution.

### Conclusion
