# Yellow Submarine - investigating layers

## Overview

## WARNING!

The results of this report are invalid due to the error in preparation of adjacency matrix. The matrix passed to Takagi decomposition should have eigenvalues between (-1, 1). However, in case of this research, some eigenvalues lied outside of this range. Some of the research has been replicated with the correct version, you can find it in `correct_report.md`.

## WARNING!

## Code 

The code is continuation of `2019_01_17_check_reproducibility`, commit hash: `aad77a501fbea913503edb14063a570e514e72aa`

The following versions of the libraries has been used:
- qmlt==0.7.1
- StrawberryFields==0.9.0

### Tensorflow problems

Due to some problems with resetting values of tensors in tensorflow, in order to run several consecutive runs, you need to use `runner.py` script instead of `main.py`.

## Description

In our scheme there are three layers of parametrizable layers: Sgates, Dgates and Non-gaussian gates (either Kerr or Cubic).
First two are followed by an interferometer.

In this experiment we were checking how different configurations of these layers work and how training performs with and without them.

Training parameters: steps: 400, learning rate: 0.1 and regularization: 1e-4.
For every combination of layers we performed 5 repetitions.

![](figures/lr_005.png)

![](figures/lr_01.png)

## Results

### Observation 1

When using non-gaussian gates only no training really occurs.

### Observation 2

Using Sgates with or without non-gaussian gates allows to get down to cost of -2.3

For the same setup with Dgates we can get down to cost of -2.8 .

### Observation 3

The value of the cubic gate parameters changes during the training - in opposition to the value of the Kerr gate parameters, which don't change at all.
Also, even when cubic gate was used, it has not influence values of trace (at least not significantly).

### Observation 4

Using both layers: Sgates and Dgates, was enough to train circuit to solve the problem. Presence of non-gaussian gates wasn't yielding any benefits.

### Conclusion

- It seems like Sgates and Dgates are enough to solve the problem at hand and it doesn't seem like non-gaussian gates are giving any boost in performance.

- The parameters of cubic gate are changing during the training, in contrast to the parameters of Kerr gates. This suggest that cubic gate actually influences the output of the circuit, even if it doesn't boost the training.

The results of this experiment suggest that cubic gate is a better choice as a non-gaussian gate for this problem than Kerr gate.