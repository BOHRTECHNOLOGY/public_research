"""Utilities used for testing."""
from itertools import permutations, product
from operator import itemgetter


def compute_all_tsp_solutions(graph):
    """Compute all possible tsp solutions using exhaustive search.

    :param graph: a NetworkX graph definining possible routes and their costs. It is
     assumed that this is a complete graph and nodes are labelled by consequtive natural
     numbers (with zero).
    :type graph: :py:class:`networkx.Graph`
    :returns: list of tuples (route, cost) sorted by cost in ascending order.
    :rtype: list
    """
    # TODO implement this method for more general case of non-complete graphs
    results = []
    for perm in permutations(list(range(1, len(graph)))):
        solution = [0] + list(perm)
        results.append((solution, calculate_cost_of_route(graph, solution)))
    return sorted(results, key=itemgetter(1))

def calculate_cost_of_route(graph, route):
    """Calculate cost of particular tsp route using weights of graph edges as costs.

    :param graph: a NetworkX graph defining possible routes and their costs. It is
     assumed that all two-node routes defined by `route` parameter exist in the graph.
    :type graph: :py:class:`networkx.Graph`
    :param route: a sequence of integers defining consequtive nodes visited in the route.
     The final node should not be present (i.e. for route 0->2->3->0 specify [0,2,3]
     not [0,2,3,0]).
    :type route: sequence of ints
    :returns: total cost of the given `route`
    :rtype: numeric, exact type depends on type of weights in `graph`
    """
    try:
        return sum(graph[route[i]][route[(i+1) % len(graph)]]['weight'] for i in range(len(graph)))
    except KeyError:
        raise ValueError('The passed route is invalid for given graph.')

def compute_all_qubo_solutions(qubo, num_qubits):
    """Compute all solutions of given QUBO.

    :param qubo: a mapping (i, j) -> coefficient defining optimization problem.
    :type qubo: dict
    :param num_qubits: number of qubits. While it is unnecessary to pass it (it might be
     deduced from `qubo`) it is usually known beforehand and passing it explicitly
     simplifies implementation.
    :type num_qubits: int
    :returns: list of couples (qubits, energy) where first element is assignment of values
     to consequtive qubits and second one is corresponding energy. The list is sorted
     in ascending order by energies.
    :rtype: list.
    """
    results = []
    for qubits in product([0,1], repeat=num_qubits):
        energy = sum(qubo[(i, j)] * qubits[int(i)] * qubits[int(j)] for i, j in qubo)
        results.append((qubits, energy))
    return sorted(results, key=itemgetter(1))
