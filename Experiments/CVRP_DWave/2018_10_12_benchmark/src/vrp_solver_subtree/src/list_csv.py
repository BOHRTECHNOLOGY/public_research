import argparse
import os
import numpy as np
import pandas as pd
import re


def import_data_from_list(path):
    '''
    Extract data from web-scrapped list.
    Args:
        path_raw_list_csv: path to raw list
    '''
    raw = pd.read_csv(path, sep=';')
    reg = re.compile(".*PNI..([0-9]+).\s*([-\"ąęćżźółńśĄŻŹĆĘÓŁŃŚa-zA-Z0-9 \./,]+)\.$")
    outposts = pd.DataFrame(columns=["name","addr", "lat","lng", "pni"])
    N = raw.shape[0]
    pnis = []
    addrs = []
    for x in raw['popupcontent']:
        m = reg.match(x)
        if m is None:
            print("Parsing failed at:", x)
            exit(1)
        g = m.groups()
        pnis.append(int(g[0]))
        addrs.append(g[1])
    outposts["lat"] = raw["lat"]
    outposts["lng"] = raw["lng"]
    outposts["name"] = raw["label"]
    outposts["pni"] = pnis
    outposts["addr"] = addrs
    return outposts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data from helper csv list.')
    parser.add_argument('list', help='Helper outposts csv list')
    parser.add_argument('--out', help='Output file')
    args = parser.parse_args()

    df_list = import_data_from_list(args.list)
    if args.out is not None:
        df_list.to_csv(args.out, sep=';')

