from __future__ import print_function
from __future__ import division
import time
import os
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
import multiprocessing
from multiprocessing import Queue, Lock

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

    handler_type = "process"
    handle = ""
    mainthread = False

    def prepare(self):
        super.prepare(self)
        self.Queue = multiprocessing.Queue()

    def deploy(self):
        pass

    def ask_and_wait(self, args_d):
        self.Queue.put(args_d)
        p = multiprocessing.Process(target=self.run)
        p.join()

    def run(self):
        args_d = self.Queue.get()
        pre_process.pre_process(
            namedtuple('Struct', args_d.keys())(*args_d.values()))


class pspnet_img_combine(task):

    handler_type = "process"
    handle = ""
    mainthread = False

    def prepare(self):
        super.prepare(self)
        self.Queue = multiprocessing.Queue()

    def deploy(self):
        pass

    def ask_and_wait(self, args_d):
        self.Queue.put(args_d)
        p = multiprocessing.Process(target=self.run)
        p.join()

    def run(self):
        args_d = self.Queue.get()
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
        misc.imsave(filename + "_seg_blended" + ext, alpha_blended)


class pspnet_dl(task):
    mainthread = True
    handler_type = 'file'
    handler = "temp_arg.json"

    def prepare(self):
        super.prepare(self)
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
        while (1):
            self.mutex.acquire()
            if not os.path.exists(self.handler):
                with open(self.handler, 'w+') as fout:
                    fout.write(json.dumps(args_d))
                self.mutex.release()
                break
            self.mutex.release()
        while (1):
            # print("waiting...")
            self.mutex.acquire()
            if not os.path.exists(self.handler):
                break
            self.mutex.release()
            time.sleep(1)
        self.mutex.release()

    def run(self):
        # print("waiting for task")
        # try:
        self.mutex.acquire()
        if os.path.exists(self.handler):
            print("received task")
            f = open(self.handler)
            json_data = f.read()
            args_d = json.loads(json_data)
            args_d['sess'] = self.sess
            args_d['model_ok'] = self.pspnet
            args_d['remote_uuid'] = self.remote_uuid
            args_d['socketIO'] = self.socketIO
            global_arg = namedtuple('Struct', args_d.keys())(*args_d.values())
            deeplearning.deep_process(global_arg)
            os.remove(self.handler)
        self.mutex.release()
        time.sleep(1)


pspnet_dl_in = pspnet_dl()
pspnet_pre_in = pspnet_pre()
pspnet_img_combine_in = pspnet_img_combine()
tasks = [pspnet_pre_in, pspnet_dl_in, pspnet_img_combine_in]

# config
config_p1_folder = './p1'
config_p2_folder = './p2'
config_p3_folder = './p3'

# init remote link
data = {
    "proxy": {
        "host": "star.eecs.oregonstate.edu",
        "username": "guxi",
        "password": "cft6&UJM",
        "port": 22,
    },
}

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None


def sshdownload(data):
    ssht = sshtunnel.SSHTunnelForwarder(
        data['proxy']['host'],
        ssh_username=data['proxy']['username'],
        ssh_password=data['proxy']['password'],
        remote_bind_address=(data['ssh']['host'], data['ssh']['port']))
    ssht.start()
    print(ssht.local_bind_port)
    sftp = pysftp.Connection(
        "127.0.0.1",
        username=data['ssh']['username'],
        password=data['ssh']['password'],
        port=ssht.local_bind_port,
        cnopts=cnopts)
    sftp.get(data['input_path'])
    ssht.stop()


def sshupload(data, path):
    ssht = sshtunnel.SSHTunnelForwarder(
        data['proxy']['host'],
        ssh_username=data['proxy']['username'],
        ssh_password=data['proxy']['password'],
        remote_bind_address=(data['ssh']['host'], data['ssh']['port']))
    ssht.start()
    print(ssht.local_bind_port)
    sftp = pysftp.Connection(
        "127.0.0.1",
        username=data['ssh']['username'],
        password=data['ssh']['password'],
        port=ssht.local_bind_port,
        cnopts=cnopts)
    sftp.chdir(data["output_path"])
    sftp.put(path)
    ssht.stop()


# global data storage
class Pspnet_namespace(BaseNamespace):
    def __init__(*argv):
        print(argv)
        super.__init__(super,*argv)

    def on_asknext(self, *args):
        self.emit("next")

    def on_request(self, *args):
        # tf.reset_default_graph()
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
        args_d['output_path'] = "{2}/{0}{1}".format(panid, ext,
                                                    config_p1_folder)

        pspnet_pre.ask_and_wait(args_d=args_d)
        print("phase 2...")
        # args_d['sess']=sess
        # args_d['model_ok']=pspnet
        args_d['input_path'] = config_p1_folder + '/'
        args_d['input_path_filter'] = panid
        args_d['output_path'] = config_p2_folder + '/'
        pspnet_dl_in.ask_and_wait(args_d)

        print("phase 3...")
        args_d['input_path'] = "./{0}{1}".format(panid, ext)
        args_d['input_path2'] = "{2}/{0}{1}".format(panid, ext,
                                                    config_p2_folder)
        args_d['output_path'] = "{2}/{0}{1}".format(panid, ext,
                                                    config_p3_folder)
        pspnet_img_combine_in.ask_and_wait(args_d)

        print("upload...")
        sshupload(data, filename + "_seg_blended" + ext)
        print("garbage cleaning")
        print("success")
        self.emit("next")


def main():
    if os.path.exists("temp_arg.json"):
        os.remove("temp_arg.json")

    #create tunnel to remote server

    asio = async_socketIO(SocketIO('localhost', 30021))

    sio_pspent_info = asio.socketIO.define(Pspnet_namespace, '/pspnet')

    asio.background()
    for task in tasks:
        task.prepare()

    while (1):
        for task in tasks:
            if task.mainthread:
                task.run()
    #mutex2.put("success",block=True)
    #except:
    #   pass


if __name__ == "__main__":
    main()
