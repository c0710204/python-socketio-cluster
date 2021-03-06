from __future__ import print_function
from __future__ import division
from task import task
import time
import numpy as np
from scipy import misc, ndimage
from apps.pspnet.pkg.pspnet import deeplearning as dpl
from apps.pspnet.pkg.pspnet.psp_tf.pspnet import PSPNet50
from collections import namedtuple
from apps.pspnet.pkg.pspnet import utils
import uuid
import multiprocessing
import logging
import sys
import json
class deeplearning(task):
    mainthread = True
    handler_type = 'Queue'
    handler = ""
    """
    all thread avaliable
    """
    def avgtime(self):
        if self.avg_count.value==0:
            return -1.0
        return self.avg_time.value/self.avg_count.value
    def uptime(self):
        return self.upcount.value
    def prepare(self):
        task.prepare(self)
        self.requestQueue = multiprocessing.Queue()
        self.responseQueue = multiprocessing.Queue()
        self.mutex = multiprocessing.Lock()
        self.avg_time=self.mg.Value('f', 0)
        self.avg_count=self.mg.Value('i', 0)
        self.upcount=self.mg.Value('i', 0)

    def ask_and_wait(self, args_d):
        self.upcount.value+=1
        local_id = "{0}".format(uuid.uuid4())
        args_d['local_id'] = local_id
        self.requestQueue.put(args_d)
        p={}
        
        while (1):
            p = self.responseQueue.get()
            if p['id'] == local_id:
                break
            self.responseQueue.put(p)
        self.upcount.value-=1
        if p['err']:
            raise IOError
        
        return p['tensor']
    """
    main Thread only
    """
    def prepare_mainthread(self):
        
        #print("|{0}|\n".format(multiprocessing.current_process().name))
        #assert(multiprocessing.current_process().name=="Process-1")
        # init tensorflow
        from keras.backend.tensorflow_backend import set_session
        from keras import backend as K
        import tensorflow as tf
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.gpu_options.per_process_gpu_memory_fraction = 0.499
        self.sess = tf.Session(config=config)
        set_session(self.sess)
        self.pspnet = PSPNet50(
            nb_classes=150,
            input_shape=(473, 473),
            weights="pspnet50_ade20k",
            path="./pspnet/weights")
    
    def run(self):
        # print("\nThread info : {0} => func {1}".format(multiprocessing.current_process().name,__file__))
        #assert(multiprocessing.current_process().name=="Process-1")
        if self.requestQueue.empty():
            time.sleep(1)
            return
        # print("waiting for task")
        # try:
        t=time.time()
        args_d = self.requestQueue.get()
        args_d['sess'] = self.sess
        args_d['model_ok'] = self.pspnet
        args_d['remote_uuid'] = self.remote_uuid
        args_d['socketIO'] = self.socketIO
        global_arg = namedtuple('Struct', args_d.keys())(*args_d.values())
        p={'id':args_d['local_id'],'tensor':None,'err':None}
        try:
            ret=dpl.deep_process(global_arg)
            p['tensor']=ret
        except Exception as e:
            p['err']=e
            print(e)
        self.avg_time.value+=time.time()-t
        self.avg_count.value+=1

        self.responseQueue.put(p)
        time.sleep(1)
