import sys
import subprocess
def main():
    if len(sys.argv)>1:
        target=sys.argv[1]
        autorestart=9999999
        if len(sys.argv)>2:
            autorestart=sys.argv[2]
        while (True):
            try:
                ret = subprocess.call("python {0}".format(target), shell=True)
                print("restarting....\n")
            except Exception as e:
                print(e)
                break
if __name__ == '__main__':
    main()
