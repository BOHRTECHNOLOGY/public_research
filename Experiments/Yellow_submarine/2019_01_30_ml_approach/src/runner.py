import sys
import subprocess

def main(n_calls):
    for i in range(int(n_calls)):
        for use_ng in [0, 1, 2]:
            subprocess.run(['python', 'main.py', str(i), str(use_ng)])

if __name__ == '__main__':
    main(sys.argv[1])
