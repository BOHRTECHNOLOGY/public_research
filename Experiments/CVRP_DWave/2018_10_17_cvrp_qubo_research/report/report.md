

# Report on optimizing CVRP constants

In the described experiment we used the following parameters when solving CVRP problem:

- number of nodes: 7
- number of graphs: 10
- number of tries: 10
- magnitude of edges: 1e0
- chain strength: 8
- cost constant: 1
- constraint constant: 4

and the target was to optimize capacity constraint constant (denoted by $`\kappa`$ in this report). Please take note that other parameters fall into the regime that provided satisfying solutions for TSP problems.

## Analysis of results
The below table shows statistics of cost function relative errors:

|   $`\kappa`$ |   mean |   std |   min |   25% |   50% |   75% |   max |
|----------:|-------:|------:|------:|------:|------:|------:|------:|
|      2.00 |  28.30 |  7.16 |  5.25 | 23.53 | 30.43 | 32.38 | 41.97 |
|      4.00 |  27.73 |  7.71 |  5.25 | 24.24 | 30.29 | 33.81 | 40.58 |
|      6.00 |  29.80 |  7.19 |  5.25 | 26.29 | 30.98 | 33.87 | 46.81 |


and the below table shows statistics of cost function percentiles:

|   $`\kappa`$ |   mean |   std |   min |   25% |   50% |   75% |    max |
|----------:|-------:|------:|------:|------:|------:|------:|-------:|
|      2.00 |  69.33 | 26.86 |  3.70 | 59.26 | 77.16 | 90.12 | 100.00 |
|      4.00 |  66.77 | 28.97 |  2.47 | 55.56 | 75.31 | 90.12 | 100.00 |
|      6.00 |  74.40 | 25.78 |  2.47 | 67.28 | 80.25 | 95.06 | 100.00 |


## Conclusions
Either there is something wrong with our parameters or with the benchmarking process, as clearly quality of solutions is below expectations