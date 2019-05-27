#!/usr/bin/env python

import sys
import subprocess

def main(matrix, n_calls):
    use_ng = 1
    use_embedding = 0
    for use_ng in [0, 1, 2]:
        for use_embedding in [0, 1]:
            for i in range(int(n_calls)):
                subprocess.run(['python', 'main.py', str(matrix), str(i), str(use_ng), str(use_embedding)])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
