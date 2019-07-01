# D-Wave small CVRP benchmarks

## Overview

The main goal of this research was to check D-Wave performance on solving CVRP in comparison to other methods - ORTools and QBSolv using Tabu search.

## Code 

The exact versions of the libraries used can be found in the `pip_freeze.txt` file in `varia` directory.

The code was based on `2018_10_16_benchmark_small_tsp` experiment.

## Description

We have benchmarked three methods of solving TSP problem:
- using D-Wave 2000Q 
- using tabu solver built in QBsolv library
- using ORTools library from Google

The config files used to produced results are in `src/configs` dir.
We tested graphs of size 5 - 9, generated randomly per experiment.


## Results & Conclusins

There is not much to write about - there were only a couple of times when we were able to find valid solutions with D-Wave or QBSolv. Most probably it means there is a bug in either:

- checking if solutions are valid
- generating QUBO.

So far we have not been able to find the source of the problem.