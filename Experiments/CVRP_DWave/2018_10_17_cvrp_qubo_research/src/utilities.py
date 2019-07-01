from itertools import islice, permutations, product
from operator import itemgetter

def partitions(num_outposts, num_vehicles):
    a = [0 for _ in range(num_outposts)]
    k = 1
    a[0] = 0
    a[1] = num_outposts-1
    while k != 0:
        x = a[k - 1] + 1
        y = a[k] - 1
        k -= 1
        while x <= y and k < num_vehicles - 1:
            a[k] = x
            y -= x
            k += 1
        a[k] = x + y
        yield a[:k + 1] + [0 for _ in range(num_vehicles-k)]

def partition_to_assignment(partition, outposts):
    iterator = iter(outposts)
    return tuple(tuple(islice(iterator, num_outposts)) for num_outposts in partition)

def iterate_assignments(num_outposts, num_vehicles):
    all_orders = permutations(range(1, num_outposts))
    all_partitions = partitions(num_outposts-1, num_vehicles)

    for partition, order in product(all_partitions, all_orders):
        yield partition_to_assignment(partition, order)

def validate_assignment(assignment, outposts, capacity):
    # We validate possible assignment of cities vehicle by vehicle
    for vehicle_assignment in assignment:
        # We terminate with negative result as soon as we encounter assignment
        # for which sum of loads in each outpost is larger than vehicle's capacity
        if sum(outposts.iloc[i]['load'] for i in vehicle_assignment) > capacity:
            return False
    return True

def calculate_total_cost(assignment, graph):
    total = 0
    for vehicle_assignment in assignment:
        route = (0,) + vehicle_assignment + (0,)
        if len(route) == 2:
            continue
        total += sum(graph[route[i]][route[i+1]]['weight'] for i in range(len(route)-1))
    return total

def compute_all_cvrp_solutions(outposts, vehicles, graph):
    results = []
    for assignment in iterate_assignments(len(outposts), len(vehicles)):
        if not validate_assignment(assignment, outposts, vehicles.iloc[0]['capacity']):
            continue
        results.append((assignment, calculate_total_cost(assignment, graph)))
    return sorted(results, key=itemgetter(1))
