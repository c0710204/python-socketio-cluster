import multiprocessing
import subprocess
def worker(i):
    subprocess.Popen("python {0}".format(i),shell=True)
def main():
    tasks=["server/sdn.py","pspnet/pspnet_serving_test.py","server/logserv.py"]
    for i in tasks:
        p = multiprocessing.Process(target=worker(i))
        p.start()
if __name__ == '__main__':
    main()
