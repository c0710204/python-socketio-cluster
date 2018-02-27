import multiprocessing
import subprocess
def worker(i):
    subprocess.Popen("python {0}".format(i),shell=True)
def main():
    p_list=[]
    try:
        tasks=["pspnet/pspnet_serving_test.py","server/logserv.py"]
        for i in tasks:
            p = multiprocessing.Process(target=worker(i))
            p.start()
        p_list.push(p)
    except Exception as e:
        for p in p_list:
            p.terminate()
if __name__ == '__main__':
    main()
