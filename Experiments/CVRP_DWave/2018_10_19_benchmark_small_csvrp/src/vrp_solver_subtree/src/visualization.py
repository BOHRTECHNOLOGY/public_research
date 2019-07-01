import matplotlib.pyplot as plt
import numpy as np
import os
import pdb

def plot_solution(results, outposts, data_path=None, file_name="plot"):
    fig, ax = plt.subplots(1)
    ax = plot_outposts(ax, outposts)
    ax = plot_routes(ax, results, outposts)
    plt.title("Total cost: " + str(results.cost.sum()))
    if data_path:
        plt.savefig(os.path.join(data_path, file_name))
    else:
        plt.show()

def plot_outposts(ax, outposts):
    for _, current_outpost in outposts.iterrows():
        ax.plot(current_outpost.latitude, current_outpost.longitude, 'bo', markersize=15)
        ax.annotate(str(current_outpost.outpost_id), xy=(current_outpost.latitude, current_outpost.longitude), ha="center", va="center")
        ax.annotate(str(current_outpost.load), xy=(current_outpost.latitude + 0.3, current_outpost.longitude + 0.3), ha="center", va="center", fontsize=8)
    return ax

def plot_routes(ax, results, outposts):
    hues = np.linspace(0, 1, num=len(results))
    colors = [[1, hue, 1-hue] for hue in hues]
    for route_id, result in results.iterrows():
        route = result.route
        for i in range(len(route) - 1):
            id_A = route[i]
            id_B = route[i + 1]
            outpost_A = outposts[outposts.outpost_id==id_A]
            outpost_B = outposts[outposts.outpost_id==id_B]
            point_A = [float(outpost_A.latitude), float(outpost_A.longitude)]
            point_B = [float(outpost_B.latitude), float(outpost_B.longitude)]
            ax.plot([point_A[0], point_B[0]], [point_A[1], point_B[1]], '-', c=colors[route_id])
    return ax