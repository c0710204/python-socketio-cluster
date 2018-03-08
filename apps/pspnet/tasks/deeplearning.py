from __future__ import print_function
from __future__ import division
from task import task
import time
import numpy as np
from scipy import misc, ndimage
from ..pkg.pspnet import deeplearning
from ..pkg.pspnet.psp_tf.pspnet import PSPNet50
from collections import namedtuple
from ..pkg.pspnet import utils
import uuid
import multiprocessing
import logging


class deeplearning(task):
    mainthread = True
    handler_type = 'Queue'
    handler = ""

    def prepare_mainthread(self):
        # init tensorflow
        from keras.backend.tensorflow_backend import set_session
        from keras import backend as K
        import tensorflow as tf
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

    def prepare(self):
        task.prepare(self)
        self.requestQueue = multiprocessing.Queue()
        self.responseQueue = multiprocessing.Queue()
        self.mutex = multiprocessing.Lock()

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
