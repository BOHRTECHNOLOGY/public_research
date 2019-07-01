#!/usr/bin/env python

import matplotlib.pyplot as plt
import argparse
from argparse import RawTextHelpFormatter
import numpy as np
import pandas as pd
import os
import ast
from xls import import_data_from_xls
from graph_generator import lat_long_to_x_y


DESCRIPTION = '''
Solution visualisation tool.
'''


def load_to_rgba(load, m, M):
    '''
    Create tuple of values coding color in RGBA using floats in [0, 1] range.
    If `load` varies between `m` and `M`, all RGA channels change linearly.
    `m` and `M` define loads corresponding to color limits.

    Args:
        load: given load
        m: minimal load 
        M: maximal load

    Returns:
        RGBA tuple
    '''
    if load < m:
        x = 0.5
    elif load > M:
        x = 0.95
    else:
        x = 0.5 + 0.45 * (load - m) / (M - m) 
    return (x, x, x, 0.9)


def draw_routes(ax, results, outposts):
    '''
    Draw routes from resulting routes.
    '''
    hues = np.linspace(0, 1, num=len(results))
    colors = [[1, hue, 1-hue] for hue in hues]
    for route_id, result in results.iterrows():
        route = result.route
        for i in range(len(route) - 1):
            id_A = route[i]
            id_B = route[i + 1]
            outpost_A = outposts[outposts['outpost_id']==id_A]
            outpost_B = outposts[outposts['outpost_id']==id_B]
            point_A = [float(outpost_A.latitude), float(outpost_A.longitude)]
            point_B = [float(outpost_B.latitude), float(outpost_B.longitude)]
            ax.plot([point_A[0], point_B[0]], [point_A[1], point_B[1]], '-.', c=colors[route_id], linewidth=1)
    return ax


def draw_outposts(ax, outposts):
    '''
    Draw outposts on the figure.

    Args:
        ax: matplotlib figure axes
        outposts: DataFrame with outposts data

    Returns:
        Axes
    '''
    for idx, current_outpost in outposts.iterrows():
        load = current_outpost.load
        marker_size = 6
        facecol = load_to_rgba(load, 0.05, 10)
        if idx is 0:
            ax.plot(current_outpost.latitude, current_outpost.longitude, 'rX', markersize=10)
        else:
            ax.plot(current_outpost.latitude, current_outpost.longitude, 'go', markersize=marker_size, markeredgewidth=0.5, markeredgecolor='black', markerfacecolor=facecol)
    return ax


def plot_routes(outposts, routes, savedir, name, title):
    '''
    Plot given routes.
    '''
    fig, ax = plt.subplots(1, figsize=(20,20))
    draw_outposts(ax, outposts)
    draw_routes(ax, routes, outposts)
    fig.suptitle(title, size=40)
    fig.tight_layout()
    savepath = os.path.join(savedir, name + '.png')
    fig.savefig(savepath)
    plt.close(fig)


def summarize(outposts, routes, orig):
    '''
    Generate summary of two solutions.

    Args:
        outposts: DataFrame of outposts
        routes: DataFrame with our solution
        orig: DataFrame with original solution

    '''
    def cost_stats(costs):
        '''
        Get global statistics of list of costs.
        '''
        return [np.sum(costs), np.min(costs), np.max(costs), np.std(costs), np.mean(costs)]


    # Change units to `km`
    stats_our = cost_stats(routes['cost'].values / 1000.)
    # This is a original cost in `km` calculated by Poczta Polska
    stats_orig = cost_stats(orig['cost'].values)

    # Calculate original routes costs summing up the edges 
    costs_orig_p2p = []
    for route_id, route in orig.iterrows():
        outposts_ids = route.route
        route_cost = 0
        for id_A, id_B in zip(outposts_ids, outposts_ids[1:]):
            outpost_A = outposts[outposts['outpost_id']==id_A]
            outpost_B = outposts[outposts['outpost_id']==id_B]
            x, y = lat_long_to_x_y(float(outpost_A.latitude), float(outpost_A.longitude),
                        float(outpost_B.latitude), float(outpost_B.longitude))
            # Change units to `km`
            route_cost += (abs(x) + abs(y)) / 1000.
        costs_orig_p2p += [route_cost]

    # This cost is a sum of weights in our graph
    stats_orig_p2p = cost_stats(costs_orig_p2p)
    columns = ['sum', 'min', 'max', 'mean', 'std', 'vehicles_used']
    data_dict = {
        'BOHR': stats_our + [len(routes)],
        'PP ORIG': stats_orig + [len(orig)],
        'PP ORIG P2P': stats_orig_p2p + [len(orig)]  
    }
    return pd.DataFrame.from_dict(data_dict, orient='index', 
            columns=columns)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=RawTextHelpFormatter)
    parser.add_argument('outposts', help='`outposts.csv` file path')
    parser.add_argument('routes', help='`routes.csv` file path')
    parser.add_argument('--orig_routes', help='CSV file containing original \n\
routing problem solutions, usualy named `orig_routes.csv`')
    parser.add_argument('--savedir', default='.', help='Save directory')
    
    args = parser.parse_args()

    outposts = pd.read_csv(args.outposts, sep=';')
    routes = pd.read_csv(args.routes, sep=';', converters={'route': ast.literal_eval})
    plot_routes(outposts=outposts, routes=routes, savedir=args.savedir, 
                name='solution', title='BOHR SOLUTION')

    if args.orig_routes is not None:
        orig = pd.read_csv(args.orig_routes, sep=';', 
                converters={'route': ast.literal_eval})
        plot_routes(outposts=outposts, routes=orig, savedir=args.savedir, 
                name='original', title='ORIGINAL SOLUTION')

        summary = summarize(outposts, routes, orig)
        summary.to_csv(os.path.join(args.savedir, 'summary.csv'), sep=';')
        with open('summary.txt', 'w') as f:
            f.write(str(summary))
            f.write('\n')
        print(summary)

