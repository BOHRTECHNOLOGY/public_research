# Yellow Submarine - ML approach

## Overview

In this experiment instead of training the circuit to solve a single graph, we took approach more akin to machine learning: we were training a single network using several different graphs and checking if it generalizes well.
This report is an updated version with a bug in preparatation of state fixed: `tanh` changed to `arctanh`.

## Code 

The code is built on top of `2019_01_23_investigating_layers`, commit hash: `aad77a501fbea913503edb14063a570e514e72aa`

You can find the versions of the libraries used in this experiment in `requirements.txt` file.
When it comes to `QMLT`, we have used a modified version of it, which has been included in this repository.

### Tensorflow problems

Due to some problems with resetting values of tensors in tensorflow, in order to run several consecutive runs, you need to use `runner.py` script instead of `main.py`.

## Description

The "machine learning" approach works as follows:

1. We pass several graphs (in the form of adjacency matrix) to the solver as input.
2. During every iteration, for every graph, we build a circuit and evaluate it.
3. The cost for given set parameters is sum of costs of outputs of all the created circuits.

We have used either one or two layers of gates.

By 1 layer we mean layer as described in this article: https://arxiv.org/abs/1806.06871. 

Graphs can be found in the appendix at the end of this report they have been constructed in such way, that every graph has different solution.

## Results

### Observation 1

Circuits were not able to find an optimal solution - independent of the non-linear gates used (or lack of them) it always learned to return the same results regardless of what graph has been embedded.

### Observation 2

Parameters of Kerr gates have been changing in both cases, which has not been previously observed.

### Observation 3

When using only 1 layer, parameters of the cubic gates diminished very close to 0 in almost all cases. This resulted in behaviour very similar to the case without any non gaussian gates.

### Observation 4

While using 2 layers, the results were still very similar as with 1 layer. However, the training process was much less smooth - there were some oscillations in the parameters of the gates and loss function.

### Observation 5

Unfortunately time needed to run the code on the hardware available to us increased significantly with adding the second layer, so it is unfeasible for now to test it using more layers.

### Observation 6

The output of the circuit was independent of the embedded graph.

### Observation 7

The results achieved are very similar in all the cases. The main difference is in the smoothness of the cost function. Below are plots for no non-gaussian gates, kerr gates and cubic gates (accordingly).

![](figures/current/ng_0.png)
![](figures/current/ng_1.png)
![](figures/current/ng_2.png)

## Conclusions

Proposed algorithm wasn't able to learn solving maxcut problem based on the input state. The results suggest that the input state was not relevant in the training process. Therefore some other methods should be implemented in order to facilitate training and help it generalize better.

## Appendix - graphs

```
[[0, 1, 1, 1],
[1, 0, 0, 0],
[1, 0, 0, 0],
[1, 0, 0, 0]]

[[0, 1, 0, 0],
[1, 0, 1, 1],
[0, 1, 0, 0],
[0, 1, 0, 0]]

[[0, 0, 1, 0],
[0, 0, 1, 0],
[1, 1, 0, 1],
[0, 0, 1, 0]]

[[0, 0, 0, 1],
[0, 0, 0, 1],
[0, 0, 0, 1],
[1, 1, 1, 0]]
```