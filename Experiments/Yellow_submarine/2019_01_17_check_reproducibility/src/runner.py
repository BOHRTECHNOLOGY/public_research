#!/usr/bin/env python

import sys
import subprocess

def main(n_calls):
    for i in range(int(n_calls)):
        subprocess.run(['python', 'main.py', str(i)])

if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except IndexError:
        print("Please specify the number of runs to perform as an argument to the runner.")
