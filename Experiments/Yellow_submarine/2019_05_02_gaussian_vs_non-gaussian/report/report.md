# Yellow Submarine - Gaussian vs non-Gaussian gates

## Overview

We seek to determine if the presence of non-Gaussian gates is beneficial to solving the maxcut problem.

## Observations

### Unweighted 4x4

- Convergence starts occuring after about 150 steps.

- The D gate magnitude varies and converges towards unique values where it stabilizes.
  The D gate phase remains more or less constant.

- The S gate magnitude starts stabilizing after about 250 steps.

- The cubic phase gate parameter starts coverging at about 150 steps towards a single value.

- The kerr gate doesn't participate in the computation.

### Unweighted 5x5

- Convergence starts occuring after about 150 steps.

- The D gate magnitude starts converging and stabilizing after about 100 steps.
  The D gate magnitude remains more or less constant.

- The S gate magnitude starts stabilizing at about 150 steps.

- The cubic phase gate parameter starts converging at about 50 steps.

- The Kerr gate doesn't participate in the computation.

### Unweighted 6x6

- Convergence starts occuring after about 100 steps.

- The D gate magnitude starts converging and stabilizing after about 100 steps.
  The D gate magnitude remains more or less constant.

- The S gate magnitude starts stabilizing at about 150 steps.

- The cubic phase gate parameter starts converging at about 50 steps.

- The Kerr gate doesn't participate in the computation.

### Weighted 4x4

- Convergence starts occuring after about 100 steps.

- The D gate magnitude varies and converges towards unique values where it stabilizes.
  The D gate phase remains more or less constant.

- The S gate magnitude starts stabilizing after 150 steps.

- The cubic phase gate parameter starts coverging at about 70 steps towards a single value.

- The kerr gate doesn't participate in the computation.

### Weighted 5x5

- Convergence starts occuring after about 100 steps.

- The D gate magnitude starts converging and stabilizing after about 100 steps.
  The D gate magnitude remains more or less constant.

- The S gate magnitude starts stabilizing at about 150 steps.

- The cubic phase gate parameter starts converging at about 60 steps.

- The Kerr gate doesn't participate in the computation.

### Weighted 6x6

- Convergence starts occuring after about 100 steps.

- The D gate magnitude starts converging and stabilizing after about 100 steps.
  The D gate magnitude remains more or less constant.

- The S gate magnitude starts stabilizing at about 150 steps.

- The cubic phase gate parameter starts converging at about 50 steps.

- The Kerr gate doesn't participate in the computation.


### Overall observations

- Stabilization of the loss and gradient norm/global norm starts at about 100 steps in general.

- The D gate magnitude starts stabilizing at about 100 steps. After stabilization, it converges towards 2 or 3 unique values.

- The phase of the D gate remains constant.

- The S gate magnitude starts stabilizing at about 150 steps. There is no convergence towards unique values as for each simulation,
the magnitude will land on different values in general.

- The phase of the S gate varies very slightly and can be considered constant for our purposes.

- The cubic phase gate participates in the computation actively and its parameters starts stabilizing sooner at about 50 steps.
It doesn't converge towards unique values but different values are yielded for each run.

- We also note that the presence of the cubic phase gate results in spikes in the gradient norm/global norm graph.

- The Kerr gate parameters remains constant for all simulations.

**Important notes**

- In the D gate, we note that the magnitude convergence tends towards 2 or 3 unique values. This needs explaining.

- In constrast to the D gate magnitude, the S gate magnitude is all over the place. This as well needs explaining.

- In both the D gate and the S gate magnitudes, the phase remains more or less constant. Let *z = x + iy* be the parameter to either gate.
  Since both magnitudes vary but their respective phases remain constant, we conclude the *x* and *y* vary in equal proportion, in other words *arctan(theta) = y/x* is constant but *y = k*x* for some proportionality constant *k*.
  Why is are both gates behaving like this?

- In the presence of the cubic phase gate, the gradient norm graph displays sudden spikes. Why is this?

### Graphs

Graphs can be found in the images folder. All the graphs are taken from the unweighted 4x4 adjacency matrices simulations but the shape is the same for every other simulation under similar parameters.

## Conclusion

The presence of the cubic phase gate doesn't yield any performance improvement over its absence.
In fact, because it introduces sudden spikes in the gradient norm/global norm, it might be detrimental to the quality of the result - please verify this because the spikes might be due to high learning.
The Kerr has no effect on the simulation at all.
One can conclude that Gaussian gates are sufficient to solve the maxcut problem on CV quantum computers.
