from __future__ import print_function
from __future__ import division

import time
import numpy as np
from scipy import misc, ndimage
from collections import namedtuple
import uuid
import multiprocessing
import logging
import sys
import json
try:
    from task import task 
    from ..pkg.pspnet import pre_process
    from ..pkg.pspnet import utils
except Exception as e:
    print(__file__,e)
    from . import task 
    from ..pkg.pspnet import pre_process
    from ..pkg.pspnet import utils

class pre(task):
    
    handler_type = "Process"
    handle = ""
    mainthread = False
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
        self.avg_time=self.mg.Value('f', 0)
        self.avg_count=self.mg.Value('i', 0)        
        self.result={}
        self.upcount=self.mg.Value('i', 0)
    def deploy(self):
        pass
        
    def ask_and_wait(self, args_d):
        self.upcount.value+=1
        local_id = "{0}".format(uuid.uuid4())
        args_d['local_id'] = local_id
        #self.requestQueue.put(args_d)
        p = multiprocessing.Process(
            target=self.run, args=(json.dumps(args_d), ))
        # print("\nThread info : {0} => func {1}".format(multiprocessing.current_process().name,__file__))
        p.start()
        p.join()        
        ret={}
        while (1):
            ret = self.responseQueue.get()
            if ret['id'] == local_id:
                break
            self.responseQueue.put(ret)
        self.upcount.value-=1
        return ret['tensor']

    def run(self, args_s):
        # print("\nThread info : {0} => func {1}".format(multiprocessing.current_process().name,__file__))
        t=time.time()
        args_d = json.loads(args_s)
        iname = args_d['panid']
        self.sio_auto(self.socketIO,'update', {'id': iname, "phase": 1, 'val': -1, 'max': -1})


        # print("{0} start pre".format(args_d['local_id']))
        ret=pre_process.pre_process(
            namedtuple('Struct', args_d.keys())(*args_d.values()))
        self.avg_time.value+=time.time()-t
        self.avg_count.value+=1
        self.responseQueue.put({'id':args_d['local_id'],'tensor':ret})
