"""Vehicle Routing Problem"""
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
import numpy as np
import networkx as nx
import pandas as pd
import pdb


def build_vehicle_route(routing, plan, outposts, vehicle_id):
    """
    Build a route for a vehicle by starting at the strat node and
    continuing to the end node. Source: https://github.com/google/or-tools/blob/master/examples/python/cvrptw_plot.py
    Args: routing (ortools.constraint_solver.pywrapcp.RoutingModel): routing.
    plan (ortools.constraint_solver.pywrapcp.Assignment): the assignment.
    customers (Customers): the customers instance.  vehicle_id (int): index of
    the vehicle
    Returns:
        (List) route: indexes of the customers for vehicle vehicle_id
    """
    vehicle_used = routing.IsVehicleUsed(plan, vehicle_id)
    print('Vehicle {0} is used {1}'.format(vehicle_id, vehicle_used))
    if vehicle_used:
        route = []
        node = routing.Start(vehicle_id)
        while not routing.IsEnd(node):
            route.append(routing.IndexToNode(node))
            node = plan.Value(routing.NextVar(node))

        route.append(routing.IndexToNode(node))
        return route
    else:
        return None


class CostEvaluator():

    def __init__(self, graph):
        self.graph = graph

    def get_cost(self, node_a, node_b):
        if node_a == node_b:
            return 0
        else:
            return self.graph.edges[(node_a, node_b)]['weight']
    
    def evaluate_route(self, route):
        if route:
            total_cost = 0
            for i in range(len(route) - 1):
                total_cost += self.get_cost(route[i], route[i+1])
            return total_cost
        else:
            return 0


class DemandEvaluator():
    def __init__(self, graph):
        self.graph = graph

    def get_demand(self, node_a, node_b):
        return self.graph.nodes.data()[node_a]["load"]

def add_capacity_constraints(routing, vehicles, demand_evaluator):
    """Adds capacity constraint"""
    routing.AddDimension(
        demand_evaluator,
        0, # null capacity slack
        int(vehicles.iloc[0].capacity), # vehicle maximum capacity
        True, # start cumul to zero
        "capacity")


def calculate_routes(outposts, vehicles, graph, starting_point=0, calculation_time=5):
    # Create Routing Model
    routing = pywrapcp.RoutingModel(len(outposts), len(vehicles), starting_point)
    cost_evaluator = CostEvaluator(graph)
    edge_evaluator = cost_evaluator.get_cost
    routing.SetArcCostEvaluatorOfAllVehicles(edge_evaluator)
    
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit_ms = int(calculation_time*1000)

    get_demand = DemandEvaluator(graph).get_demand
    add_capacity_constraints(routing, vehicles, get_demand)
    # Solve the problem.

    assignment = routing.SolveWithParameters(search_parameters)
    
    # If program finished due to timeout without finding a solution:
    if routing.status() == 3:
        print("Running again for a longer time")
        search_parameters.time_limit_ms *= 5
        assignment = routing.SolveWithParameters(search_parameters)

    # If program finished without finding a solution.
    # See list of status codes: https://developers.google.com/optimization/routing/routing_options
    if routing.status() != 1:
        print("Finished without finding a solution with status: ", routing.status())
        return None

    all_routes = []
    for _, vehicle in vehicles.iterrows():
        vehicle_id = int(vehicle.vehicle_id)
        route = build_vehicle_route(routing, assignment, outposts, vehicle_id)
        if route:
            cost = cost_evaluator.evaluate_route(route)
            all_routes.append([vehicle_id, route, cost])

    all_routes_df = pd.DataFrame(all_routes, columns=["vehicle_id", "route", "cost"])
    return all_routes_df

