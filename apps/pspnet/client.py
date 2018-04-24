import apps.streetdownloader.pkg.streetview as streetview
from src.libs.app.client import app_client
from tasks.pre import pre
from tasks.deeplearning import deeplearning
from tasks.image_combine import image_combine
import multiprocessing
import sys
from os.path import splitext, join, isfile, basename
from os import environ
from math import ceil
import subprocess
import logging
import json
# config
config_p1_folder = '/dev/shm/guxi/p1'
config_p2_folder = '/dev/shm/guxi/p2'
config_p3_folder = '/dev/shm/guxi/p3'

# init remote link
data = {
    "proxy": {
        "host": "star.eecs.oregonstate.edu",
        "username": "guxi",
        "password": "cft6&UJM",
        "port": 22,
    },
}


def ftunnel(*args):
    client = args[-1]
    if type(client) == dict:
        client = namedtuple('Struct', client.keys())(*client.values())
    cmd = "ssh -NR {0}:{1}:{2} {3}@{4} -p {5} >/dev/null".format(
        args[0], args[1], args[2], client.username, client.host, client.port)
    logging.info(cmd)
    ret = subprocess.call(cmd, shell=True)


def scp_download(port, user, host, path):
    cmd = "scp -P {0} {1}@{2}:{3} ./".format(port, user, host, path)
    logging.info(cmd)
    ret = subprocess.call(cmd, shell=True)


def scp_upload(port, user, host, path, file):
    cmd = "scp -P {0} ./{4} {1}@{2}:{3} ".format(port, user, host, path, file)
    logging.info(cmd)
    ret = subprocess.call(cmd, shell=True)


mutex_ssh = multiprocessing.Lock()


def sshdownload(data):
    global mutex_ssh
    mutex_ssh.acquire()

    print("downloading {0}...".format(data['input_path']))
    sys.stdout.flush()
    scp_download(data['ssh']['port'], data['ssh']['username'], data['ssh']['host'],
                 data['input_path'])
    # p.terminate()
    mutex_ssh.release()


def sshupload(data, path):
    import os
    if not os.path.exists(path):
        raise FileNotFoundError("{0} not exists".format(path))
    global mutex_ssh
    mutex_ssh.acquire()
    print("uploading {0}...".format(data['input_path']))
    sys.stdout.flush()
    scp_upload(data['ssh']['port'], data['ssh']['username'], data['ssh']['host'],
               data["output_path"], path)
    # p.terminate()
    mutex_ssh.release()


def task_process(args,pspnet_pre_in,pspnet_dl_in,pspnet_img_combine_in):
    print("got request")
    data = args[0]
    filename, ext = splitext(data['input_path'])
    panid = basename(filename)
    # download file from upper server
    print("download...")
    sys.stdout.flush()
    sshdownload(data)
    args_d = {}
    args_d['panid'] = panid
    args_d['filename'] = filename
    args_d['ext'] = ext

    args_d['model'] = "pspnet50_ade20k"

    args_d['sliding'] = True
    args_d['flip'] = True
    args_d['multi_scale'] = True

    print("phase 1...")
    sys.stdout.flush()
    args_d['input_path'] = "./{0}{1}".format(panid, ext)
    args_d['output_path'] = "{2}/{0}{1}".format(panid, ext, config_p1_folder)

    pspnet_pre_in.ask_and_wait(args_d=args_d)
    print("phase 2...")
    sys.stdout.flush()
    # args_d['sess']=sess
    # args_d['model_ok']=pspnet
    args_d['input_path'] = config_p1_folder + '/'
    args_d['input_path_filter'] = panid
    args_d['output_path'] = config_p2_folder + '/'
    pspnet_dl_in.ask_and_wait(args_d)

    print("phase 3...")
    sys.stdout.flush()
    args_d['input_path'] = "./{0}{1}".format(panid, ext)
    args_d['input_path2'] = "{2}/{0}{1}".format(panid, ext, config_p2_folder)
    args_d['output_path'] = "{2}/{0}{1}".format(panid, ext, config_p3_folder)
    pspnet_img_combine_in.ask_and_wait(args_d)

    print("upload...")
    sys.stdout.flush()
    import numpy as np
    import os
    sshupload(data, "{0}.npy".format(panid))
    l=np.load("{0}_classify.npy".format(panid)).tolist()
    print("garbage cleaning")
    os.remove("{0}.npy".format(panid))
    os.remove("{0}_classify.npy".format(panid))
    os.remove("{0}.jpg".format(panid))
    sys.stdout.flush()
    import json
    return {'panid':panid,"percent":json.dumps(l),'id':data['taskid']};

class pspnet_app_client(app_client):
    def mainthread(self):
        print("pspnet.app.client mainthread start...")
        sys.stdout.flush()
        for task in self.tasks:
            if task.mainthread:
                task.prepare_mainthread()
        print("pspnet.app.client mainthread started...")
        sys.stdout.flush()
        self.is_ready.release()
        while (1):
            for task in self.tasks:
                if task.mainthread:
                    task.run()
    def prepare(self):
        self.is_ready=multiprocessing.Lock()
        self.is_ready.acquire()
        self.tasks=[pre(),deeplearning(),image_combine()]
        for task in self.tasks:
            task.prepare()
        p=multiprocessing.Process(target=self.mainthread)
        p.start()
        print("client ready...")
        self.is_ready.acquire()
        self.run_ready.release()
    def run(self,args):
        """
        :param args all needed data from server
        """
        #print("receive {0}".format(args))
        sys.stdout.flush()
        return task_process([args],self.tasks[0],self.tasks[1],self.tasks[2])


def handler():
    return pspnet_app_client
def main():
    pass
if __name__ == '__main__':
    main()
