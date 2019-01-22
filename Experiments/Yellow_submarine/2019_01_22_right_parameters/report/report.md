# Yellow Submarine - reproducibility

## Overview


## Code 

The code is continuation of `2019_01_17_check_reproducibility`, commit hash: `aad77a501fbea913503edb14063a570e514e72aa`

The following versions of the libraries has been used:
- qmlt==0.7.1
- StrawberryFields==0.9.0

### Tensorflow problems

Due to some problems with resetting values of tensors in tensorflow, in order to run several consecutive runs, you need to use `runner.py` script instead of `main.py`.
