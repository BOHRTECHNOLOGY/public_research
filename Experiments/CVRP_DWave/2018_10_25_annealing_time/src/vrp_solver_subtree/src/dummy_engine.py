import pandas as pd
import pdb

def calculate_routes(outposts, vehicles, graph, starting_point=0):
    all_routes = []
    visited_outposts = [starting_point]
    for _, vehicle in vehicles.iterrows():
        current_outpost = starting_point
        current_capacity = vehicle.capacity
        route_cost = 0
        route = [starting_point]
        route_finished = False

        while route_finished == False:
            for edge in graph.edges(current_outpost):
                next_outpost = sorted(edge)[1]
                next_outpost_load = graph.nodes.data()[next_outpost]["load"]
                if next_outpost in visited_outposts:
                    pass
                elif next_outpost_load > current_capacity:
                    continue
                else:
                    current_capacity = current_capacity - next_outpost_load
                    current_outpost = next_outpost
                    visited_outposts.append(next_outpost)
                    route.append(current_outpost)
                    route_cost += graph.edges[edge]['weight']
                    break

            finish_condition_1 = current_capacity <= 0
            finish_condition_2 = len(visited_outposts) == graph.number_of_nodes()
            all_outpost_ids = list(outposts.outpost_id)
            not_visited_outposts = list(set(all_outpost_ids) - set(visited_outposts))
            finish_condition_3 = True
            for outpost in not_visited_outposts:
                if graph.nodes.data()[outpost]["load"] <= current_capacity:
                    finish_condition_3 = False

            if  finish_condition_1 or finish_condition_2 or finish_condition_3:
                route.append(starting_point)
                route_cost += graph.edges[(starting_point,current_outpost)]['weight']
                route_finished = True

        all_routes.append([vehicle.vehicle_id, route, route_cost])
        if len(visited_outposts) == graph.number_of_nodes():
            break
    all_routes_df = pd.DataFrame(all_routes, columns=["vehicle_id", "route", "cost"])
    return all_routes_df


