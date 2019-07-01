#!/usr/bin/env python
import argparse
import os
import pandas as pd

def generate_vehicles(veh_data):
    '''
    Generate dataframe with vehicles load.

    Args:
        veh_data: list of tuples (cap, k); cap - capacity in tons, k - number of vehicles

    Returns:
        Dataframe of vehicles data with columns [`vehicle_id`, `capacity`]
    '''
    vehicles = pd.DataFrame(columns=["vehicle_id", "capacity"])
    vehicles['vehicle_id'] = range(sum([k for _, k in veh_data]))
    capacities = []
    for c, k in veh_data:
        capacities += [c] * k
    vehicles['capacity'] = capacities
    return vehicles


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vehicles list generator')
    parser.add_argument('-e', action='append', help='Vehicle generator entry. \
            Each use of this flag will generate `k` new vehicles of load `load` tons, \
            where `k` is integer and `load` is float value.', metavar='k:load')
    parser.add_argument('--savedir', help='Save `vehicles.csv` in given directory', default='.')

    args = parser.parse_args()
    if len(args.e) == 0:
        print('No entries!')
        exit(0)

    gen_data = [(float(c), int(k)) for k, c in [tuple(x.split(':')) for x in args.e]]
    vehicles = generate_vehicles(gen_data)
    path = os.path.join(args.savedir, 'vehicles.csv')
    vehicles.to_csv(path, sep=';')

