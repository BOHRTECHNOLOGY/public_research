import sys
import subprocess

def main(n_calls):
    for i in range(int(n_calls)):
        for use_s in [1]:
            for use_d in [1]:
                for use_ng in [0, 1, 2]:
                    if use_s+use_d+use_ng == 0:
                        continue
                    subprocess.run(['python', 'main.py', str(i), str(use_s), str(use_d), str(use_ng)])
    # use_s = 1
    # use_d = 1
    # use_ng = 1
    # for i in range(int(n_calls)):
    #     subprocess.run(['python', 'main.py', str(i), str(use_s), str(use_d), str(use_ng)])

if __name__ == '__main__':
    main(sys.argv[1])
