# Yellow Submarine - finding parameters

## Overview

The main objective of this experiment was to find the right values of learning rate and regularization.

## Code 

The code is continuation of `2019_01_17_check_reproducibility`, commit hash: `aad77a501fbea913503edb14063a570e514e72aa`

The following versions of the libraries has been used:
- qmlt==0.7.1
- StrawberryFields==0.9.0

### Tensorflow problems

Due to some problems with resetting values of tensors in tensorflow, in order to run several consecutive runs, you need to use `runner.py` script instead of `main.py`.

## Description

In this experiment we based on the knowledge we gained from the previous version (see `old_report.md`). Hence, we were testing learning rates from the following set: [0.1, 0.25, 0.5] and regularization value from: [1e-4, 1e-3, 1e-2, 1e-1].


## Results

### Observation 1

With regularization 0.1 values of most of the parameters went down to 0.
With regularization 0.01 they were clearly diminishing over time. 
For smaller values the effect was hard to notice.

### Observation 2

Trace was well preserved in all the simulations.

### Observation 3

For learning rate 0.1 training converged after 150 steps.
For learning rate 0.25 training converged after 100 steps.
For learning rate 0.5 training converged after 50 steps.

### Observation 4

Some simple tests of learning rate 1.0 showed, that the loss function was very ragged.


### Observation 5

Lower values of regularization yielded faster convergence and better results.

### Observation 6

In majority of cases the circuits learned to predict correct output with certainty of 90% or more.

### Conclusion

After analyzing the results of this experiment, we have decided to use the following parameters for further research: learning rate 0.25 and regularization strength 1e-3.