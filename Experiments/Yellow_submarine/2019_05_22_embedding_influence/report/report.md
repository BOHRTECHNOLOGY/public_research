# Yellow Submarine - Embedding influence

## Overview

The goal of this experiment was to determine what is the influence of using embedded graph in the optimization process.

## Description

We have done simulations using weighted and unweighted graphs from the previous experiment (`2019_05_02_gaussian_vs_non-gaussian`).

For each matrix we have performed 10 simulations - 5 with the embedding part of the circuit and 5 without it.

## Observations

### Observation 1

In all cases, in the present of the embedding the final value of the cost function was either slightly worse or the same as without it. The difference in the value of the cost function was of order of few percents.

### Observation 2

In the case of 4x4 matrices the differences were stronger than for bigger matrices - the final value of the cost function in the presence of the embedding was about 10% higher.
The convergence was also slower - without the embedding part optimization converged after 50 iterations, with the embedding part it was 50-100 iterations.

### Observation 3

There was no clear influence of the embedding on the training process, except the 4x4 matric case.

### Observation 4

The effects described earlied don't seem to correlate with the type of the non-Gaussian gate used.

### Observation 5

We have not observed any effects of the presence/absence of embedding on the paramaters of gates used.

## Conclusion

It seems that the presence of the embedding has no positive effect on the results of the algorithm and might have some detrimental effects:

- the circuit uses more gates,
- algorithm might converge to higher value of the cost function,
- convergence might be slower.