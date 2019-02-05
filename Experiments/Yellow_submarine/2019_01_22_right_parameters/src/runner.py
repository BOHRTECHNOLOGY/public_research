import sys
import subprocess

def main(n_calls):
    # lr_list = [0.05, 0.1, 0.15]
    # reg_list = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    # for i in range(int(n_calls)):
    #     for lr in lr_list:
    #         for reg in reg_list:
    #             print("LR", lr, "REG", reg, "id:", i)
    #             subprocess.run(['python', 'main.py', str(i), str(lr), str(reg)])

    lr = 0.1
    reg = 0.0001
    for i in range(int(n_calls)):
        print("LR", lr, "REG", reg, "id:", i)
        subprocess.run(['python', 'main.py', str(i), str(lr), str(reg)])

if __name__ == '__main__':
    main(sys.argv[1])
