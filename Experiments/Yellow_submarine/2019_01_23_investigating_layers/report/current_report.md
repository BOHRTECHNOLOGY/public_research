# Yellow Submarine - investigating layers

## Overview

The main goal of this experiment was to investigate how the non-gaussian layers influence the output.

## Code 

The code is continuation of `2019_01_17_check_reproducibility`, commit hash: `aad77a501fbea913503edb14063a570e514e72aa`

The following versions of the libraries has been used:
- qmlt==0.7.1
- StrawberryFields==0.9.0

### Tensorflow problems

Due to some problems with resetting values of tensors in tensorflow, in order to run several consecutive runs, you need to use `runner.py` script instead of `main.py`.

## Description

In our scheme there are three layers of parametrizable layers: Sgates, Dgates and Non-gaussian gates (either Kerr or Cubic).
First two are preceded by an interferometer.

In this experiment we checked how the last layer influences the results.

Training parameters: steps: 300, learning rate: 0.1 and regularization: 1e-4.
For every combination of layers we performed 7 repetitions.


## Results


### Observation 1

The value of the cubic gate parameters changes during the training - in opposition to the value of the Kerr gate parameters, which don't change at all.
Also, even when cubic gate was used, it has not influence values of trace (at least not significantly).

### Observation 2

Presence of non-gaussian layers improved the performance of the circuit - the convergence was somewhat faster. 
However in most cases using only Sgates and Dgates was also enough to solve the problem.

### Observation 3

There wasn't much difference between the performance while using Kerr gates or Cubic gates.

### Conclusion


- The parameters of cubic gate are changing during the training, in contrast to the parameters of Kerr gates. This suggest that cubic gate actually influences the output of the circuit, even if it doesn't boost the training.

The results of this experiment suggest that cubic gate is a better choice as a non-gaussian gate for this problem than Kerr gate.