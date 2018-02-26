from __future__ import print_function
from __future__ import division
import time
import os
import subprocess
from os.path import splitext, join, isfile, basename
from os import environ
from math import ceil
import argparse
import numpy as np
from scipy import misc, ndimage
import pre_process
import deeplearning
import img_combine2
from psp_tf.pspnet import PSPNet50
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from async_socketIO import async_socketIO
from collections import namedtuple
import sshtunnel
import pysftp
import utils
import uuid
import json
import tqdm
import multiprocessing
from multiprocessing import Queue, Lock
import logging
# init tensorflow
from keras.backend.tensorflow_backend import set_session
from keras import backend as K
import tensorflow as tf
# init global lock
mutex = Lock()
mutex1 = Queue(1)
mutex2 = Queue(1)
mutex_data = None

# end init global lock


class task():
    """
    mainthread:

        True    : need to maintain the run() in the main thread to provide service
        False   : auto create process to provide service

    handler_type:

        "file"  : using file as status and args transfer tool
        "queue" : build-in queue transfer



    """
    mainthread = False
    handler_type = 'None'

    def prepare(self):
        """
        using to init before running code
        """
        self.remote_uuid = "{0}{1}".format(uuid.uuid4(), "_deeplearning")
        self.socketIO = SocketIO('localhost', 30001, LoggingNamespace)


class pspnet_pre(task):

    handler_type = "Process"
    handle = ""
    mainthread = False

    def prepare(self):
        task.prepare(self)

    def deploy(self):
        pass

    def ask_and_wait(self, args_d):
        local_id = "{0}".format(uuid.uuid4())
        print(local_id)
        args_d['local_id'] = local_id
        p = multiprocessing.Process(
            target=self.run, args=(json.dumps(args_d), ))
        p.start()
        p.join()

    def run(self, args_s):
        args_d = json.loads(args_s)
        print("{0} start pre".format(args_d['local_id']))
        pre_process.pre_process(
            namedtuple('Struct', args_d.keys())(*args_d.values()))


class pspnet_img_combine(task):

    handler_type = "Queue"
    handle = ""
    mainthread = False

    def prepare(self):
        task.prepare(self)
        self.requestQueue = multiprocessing.Queue()
        self.responseQueue = multiprocessing.Queue()

    def deploy(self):
        pass

    def ask_and_wait(self, args_d):
        local_id = "{0}".format(uuid.uuid4())
        args_d['local_id'] = local_id
        p = multiprocessing.Process(
            target=self.run, args=(json.dumps(args_d), ))
        p.start()
        p.join()

    def run(self, args_s=""):
        args_d = json.loads(args_s)
        panid = args_d['panid']
        ext = args_d['ext']
        filename = args_d['filename']
        class_scores = img_combine2.img_combine2(
            namedtuple('Struct', args_d.keys())(*args_d.values()))
        print("blended...")
        img = misc.imread("./{0}{1}".format(panid, ext))
        img = misc.imresize(img, 10)

        class_image = np.argmax(class_scores, axis=2)
        pm = np.max(class_scores, axis=2)
        colored_class_image = utils.color_class_image(class_image,
                                                      args_d['model'])
        #colored_class_image is [0.0-1.0] img is [0-255]
        alpha_blended = 0.5 * colored_class_image + 0.5 * img
        misc.imsave(panid + "_seg_blended" + ext, alpha_blended)
        # for filename in tqdm.tqdm(os.listdir('/tmp')):
        #     if filename.endswith(".npy"):
        #         try:
        #             os.remove(filename)
        #         except Exception:
        #             pass
        self.responseQueue.put(args_d['local_id'])


class pspnet_dl(task):
    mainthread = True
    handler_type = 'Queue'
    handler = ""

    def prepare(self):
        task.prepare(self)
        self.requestQueue = multiprocessing.Queue()
        self.responseQueue = multiprocessing.Queue()
        self.mutex = multiprocessing.Lock()
        config = tf.ConfigProto()
        # config.gpu_options.allow_growth = True
        # config.gpu_options.per_process_gpu_memory_fraction = 0.4
        self.sess = tf.Session(config=config)
        set_session(self.sess)
        self.pspnet = PSPNet50(
            nb_classes=150,
            input_shape=(473, 473),
            weights="pspnet50_ade20k",
            path="./pspnet/weights")

        # end

    def ask_and_wait(self, args_d):
        local_id = "{0}".format(uuid.uuid4())
        args_d['local_id'] = local_id
        self.requestQueue.put(args_d)
        while (1):
            p = self.responseQueue.get()
            if p == local_id:
                break
            self.responseQueue.put(p)

    def run(self):
        # print("waiting for task")
        # try:
        args_d = self.requestQueue.get()
        args_d['sess'] = self.sess
        args_d['model_ok'] = self.pspnet
        args_d['remote_uuid'] = self.remote_uuid
        args_d['socketIO'] = self.socketIO
        global_arg = namedtuple('Struct', args_d.keys())(*args_d.values())
        deeplearning.deep_process(global_arg)
        self.responseQueue.put(args_d['local_id'])
        time.sleep(1)


pspnet_dl_in = pspnet_dl()
pspnet_pre_in = pspnet_pre()
pspnet_img_combine_in = pspnet_img_combine()
tasks = [pspnet_pre_in, pspnet_dl_in, pspnet_img_combine_in]

# config
config_p1_folder = '/dev/shm/p1'
config_p2_folder = '/dev/shm/p2'
config_p3_folder = '/dev/shm/p3'

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
    #start tunnel
    # tunnel_p = multiprocessing.Process(
    #     target=ftunnel,
    #     args=(50033, data['ssh']['host'], data['ssh']['port'], data['proxy']))
    # tunnel_p.start()
    #do scp_download
    print("downloading {0}...".format(data['input_path']))
    scp_download(data['ssh']['port'], data['ssh']['username'], "127.0.0.1",
                 data['input_path'])
    # p.terminate()
    mutex_ssh.release()


def sshupload(data, path):
    global mutex_ssh
    mutex_ssh.acquire()
    #start tunnel
    # tunnel_p = multiprocessing.Process(
    #     target=ftunnel,
    #     args=(50033, data['ssh']['host'], data['ssh']['port'], data['proxy']))
    # tunnel_p.start()
    #do scp_download
    print("uploading {0}...".format(data['input_path']))
    scp_upload(data['ssh']['port'], data['ssh']['username'], "127.0.0.1",
               data["output_path"], path)
    # p.terminate()
    mutex_ssh.release()


def task_process(args, sio):
    print("got request")
    data = args[0]
    filename, ext = splitext(data['input_path'])
    panid = basename(filename)
    # download file from upper server
    print("download...")
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
    args_d['input_path'] = "./{0}{1}".format(panid, ext)
    args_d['output_path'] = "{2}/{0}{1}".format(panid, ext, config_p1_folder)

    pspnet_pre_in.ask_and_wait(args_d=args_d)
    print("phase 2...")
    # args_d['sess']=sess
    # args_d['model_ok']=pspnet
    args_d['input_path'] = config_p1_folder + '/'
    args_d['input_path_filter'] = panid
    args_d['output_path'] = config_p2_folder + '/'
    pspnet_dl_in.ask_and_wait(args_d)

    print("phase 3...")
    args_d['input_path'] = "./{0}{1}".format(panid, ext)
    args_d['input_path2'] = "{2}/{0}{1}".format(panid, ext, config_p2_folder)
    args_d['output_path'] = "{2}/{0}{1}".format(panid, ext, config_p3_folder)
    pspnet_img_combine_in.ask_and_wait(args_d)

    print("upload...")
    sshupload(data, panid + "_seg_blended" + ext)
    print("garbage cleaning")

    print("success")
    sio.emit("next", data)


# global data storage
class Pspnet_namespace(BaseNamespace):
    def on_asknext(self, *args):
        self.emit("next", None)

    def on_request(self, *args):
        p = multiprocessing.Process(target=task_process, args=(args, self))
        p.start()


def main():
    if os.path.exists("temp_arg.json"):
        os.remove("temp_arg.json")

    for task in tasks:
        task.prepare()
    asio = async_socketIO(SocketIO('localhost', 30021))

    sio_pspent_info = asio.socketIO.define(Pspnet_namespace, '/pspnet')

    asio.background()

    while (1):
        for task in tasks:
            if task.mainthread:
                task.run()
    #mutex2.put("success",block=True)
    #except:
    #   pass


if __name__ == "__main__":
    main()
