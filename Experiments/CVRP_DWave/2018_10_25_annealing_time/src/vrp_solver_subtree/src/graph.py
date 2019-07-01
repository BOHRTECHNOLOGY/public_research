#!/usr/bin/env python
'''
Graph generator.

Script generates `graph.csv` file using previously created `outpost.csv` file.

Usage:
    /path/to/graph.sh <outpost.csv path> [--savedir directory] [--gmaps]
'''

import pandas as pd
import numpy as np
import os
import argparse
from gmaps import GMaps
from graph_generator import GraphGenerator


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate graph description.')
    parser.add_argument('outposts', help='Path to `outposts.csv` file.')
    parser.add_argument('--savedir', help='Directory to save in - default: `.`', default='.')
    parser.add_argument('--gmaps', action='store_true', 
            help='Use Google Maps when calculating distances.')
    args = parser.parse_args()

    df_o = pd.read_csv(args.outposts, sep=';')
    ggen = GraphGenerator(df_o, gmaps=args.gmaps)
    ggen.graph_df.to_csv(os.path.join(args.savedir, 'graph.csv'), sep=';')

