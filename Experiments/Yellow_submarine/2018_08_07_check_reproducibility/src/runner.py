import sys
import subprocess

def main(n_calls):
    for i in range(int(n_calls)):
        subprocess.run(['python', 'main.py', str(i)])

if __name__ == '__main__':
    main(sys.argv[1])
