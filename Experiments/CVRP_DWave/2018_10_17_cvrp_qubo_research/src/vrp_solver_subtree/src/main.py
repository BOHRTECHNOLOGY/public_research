import os
import data_importer
import dummy_engine, ortools_engine, dwave_engine
import pdb
import utilities
import time
import visualization

def main():
    data_path = os.path.join("..", "data", "generated_at_" + str(int(time.time())))
    outposts, vehicles, graph = utilities.generate_input(6, data_path)
    # data_path = os.path.join("..", "data", "dummy_data")
    # data_path = os.path.join("..", "data", "triangle_case")
    results_path = os.path.join(data_path, "results")
    os.makedirs(results_path, exist_ok=True)

    
    outposts, vehicles, graph = data_importer.import_all_data(data_path)
    starting_point = 0 
    start_time = time.time()
    dwave_results = dwave_engine.calculate_routes(outposts, vehicles, graph, starting_point)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("DWave calculation time:", calculation_time)
    if dwave_results is not None:
        dwave_results.to_csv(os.path.join(results_path, "dwave_routes.csv"), sep=";", index_label="route_id")
        visualization.plot_solution(dwave_results, outposts, results_path, file_name="dwave_plot")

    starting_point = 0
    dummy_results = dummy_engine.calculate_routes(outposts, vehicles, graph, starting_point)
    dummy_results.to_csv(os.path.join(results_path, "dummy_routes.csv"), sep=";", index_label="route_id")
    visualization.plot_solution(dummy_results, outposts, results_path, file_name="dummy_plot")

    start_time = time.time()
    or_results = ortools_engine.calculate_routes(outposts, vehicles, graph, starting_point, calculation_time=calculation_time)
    end_time = time.time()
    calculation_time = end_time - start_time
    print("ORTools calculation time:", calculation_time)
    if or_results is not None:
        or_results.to_csv(os.path.join(results_path, "ortools_routes.csv"), sep=";", index_label="route_id")
        visualization.plot_solution(or_results, outposts, results_path, file_name="ortools_plot")

if __name__ == '__main__':
    main()
