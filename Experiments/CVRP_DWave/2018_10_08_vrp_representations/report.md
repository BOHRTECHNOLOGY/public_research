# VRP representations - report

## Overview

We have done research on different representations of TSP and VRP problems in QUBO formulation for D-Wave machines. This report summarizes the main lessons learned.

We encode all the solutions as bitstrings. Size of the bitstring depends both on the problem size and given representation.


## Code

We've been working on this topic for a couple of weeks and tried different approaches. However, since our approach was exploratory, we have not documented it properly on different stages. 

## A. TSP edges representation

### Description
Each bit represents an edge in graph. If it's equal to one it means that we use given edge in the solution.

It is inspired by the example notebook from D-Wave, TSP-7.

### Qubo formulation

In this approach we use two types of costs:
- elements on the diagonal encode the cost of the solution.
- other elements encode the constraint that we can use only two edges coming out from one node.

### Pros and cons

One huge advantage of this solution is that for undirected graph it scales as N^2/2, which is much better than (N-1)^2 scaling in other representations. The other is its simplicity.

However, the main disadvantage is that it allows for existence of subloops - i.e. we can have a solution where there are separate loops. To overcome this we would need to introduce either higher-order variables (we have only 2nd order interactions in qubo) or using integer variable (we have only binary variables in qubo). It makes this approach much more complicated and seems to require huge number of ancilla qubits.

## B. TSP time-city representation

### Description
Here we have N strings of N bits. Each string represents one time step. Inside each time step each bit represents one city. This solution scales like N^2 (or (N-1)^2 with small improvement).

### Qubo formulation

In this approach we use the following types of costs:
- Cost associated with choosing given city - this is actually a reward, huge negative number.
- Constraint that in given timestep we can be only in one city
- Constraint that we can visit each city once
- Cost of travelling between cities

In addition to that we can encode the cost to the starting and final city (if they are specified) which allows us to reduce scaling to (N-1)^2.

### Pros and cons

This representation allows us to omit the problem with the subloops. It is also easy to interpret and it's relatively easy to encode capacity constraints with it.

The main drawback is that this approach scales poorly with the number of qubits.

## C. VRP edges representation

### Description

This was a hack on A, where we used its property of forming subloops. It allowed for solving VRP with identical vehicles.

### Qubo formulation

Same as for A, but I've changed the constraint for the starting node, so there could have been more edges exiting this node. Hence, it forced the solution to form multiple loops. 

### Pros and cons

This approach is very compact and scales as N^2/2.

However, there are two issues: it still allows for the subloops and we are not sure how to encode capacity constraints here.

## D. VRP time-city representation

### Description

In this approach we use M (number of vehicles) instances of A representations and add some global constraints.

### Qubo formulation

Every vehicles has its own B representation. On top of that we add global constraints which restrict visiting the same cities if other vehicle already visited it.

### Pros and cons

Mainly cons. There are several issues with this. One is an additional layer of constraints, which makes it harder to tune the parameters. Another is the problem with representation and constraints - this approach requires changes in encoding, i.e. existence of gaps in some routes. 
Also, this approach requires M\*N^2, which makes it scale badly.

## E. VRP time-city representations with vehicle partition

If we knew the number of cities each vehicle should visit, we could encode whole problem very similarly to the B representation. We will divide QUBO matrix of size (N-1)^2 into sections corresponding to each vehicle.

### Qubo formulation
Given a partition (a, b, c, ...) for M vehicles, where a,b,c, ... are integers representing how many cities should a vehicle visit, we can construct a QUBO similarly as we did in case B:

- Cost associated with choosing given city - this is actually a reward, huge negative number.
- Constraint that in given timestep we can be only in one city
- Constraint that we can visit each city once
- Cost of travelling between cities

However, we need to introduce the following changes:
- Since first a\*N qubits represent first vehicle and the next b\*N the next one, we do not include cost of travelling between qubits a\*(N-1) - a\*(N)  and a\*N+1 - (a\*N)+N (similarly for the following partitions).
- Cost of travelling to the depot needs to be included for every N qubits starting and ending every partition.

We used the (N-1)^2 representation to simplify the matrix - we don't need to care about different constraints for visiting depot M times.

### Pros and cons

The main advantage of this approach is that the number of qubits required scales as (N-1)^2 and is independent of the number of vehicles. It's also doesn't add any additional constraints that we need to encode into QUBO and is easy to implement.

On the other hand, it works only for the specified partition and number of possible partitions is equal to (N over M) (binomial coefficient), though it's slightly better if we assume that all the vehicles are identical. For this approach to be used in any practical setting, we would need to use some heuristics to limit number of possible partitions to a reasonable subset.

## F. CVRP time-city representations with vehicle partition

This is the same as representation E, only capacity constraints are added.

### QUBO formulation

To encode capacity constraints we use the following transformation:
(x1 + x2 + x3) <= 1   ->  P(x1\*x2 + x1\*x3 + x2\*x3)

Source: http://www.info.univ-angers.fr/~hao/papers/JOCO2014.pdf

By using this constraints for every vehicle, we have our QUBO formulation of CVRP.

### Pros and cons

This approach has the same pros and cons as E. However, when it comes to choosing the partitions, we can probably use information about loads and capacities to exclude some partitions right away.

## Summary

Several methods of solving TSP anc (c)VRP has been tested and implemented. In the end we decided to use method F, since it is most compact in the number of qubits and gives correct results even without much tuning of the parameters.
