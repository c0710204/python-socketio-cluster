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
    def uptime(self):
        return self.upcount
    def prepare(self):
        
        task.prepare(self)
        self.requestQueue = multiprocessing.Queue()
        self.responseQueue = multiprocessing.Queue()
        self.result={}

    def deploy(self):
        pass
        
    def ask_and_wait(self, args_d):
        self.upcount+=1
        local_id = "{0}".format(uuid.uuid4())
        args_d['local_id'] = local_id
        #self.requestQueue.put(args_d)
        p = multiprocessing.Process(
            target=self.run, args=(json.dumps(args_d), ))
        p.start()
        p.join()        
        ret={}
        while (1):
            ret = self.responseQueue.get()
            if ret['id'] == local_id:
                break
            self.responseQueue.put(ret)
        self.upcount-=1
        return ret['tensor']

    def run(self, args_s):
        args_d = json.loads(args_s)
        iname = args_d['panid']
        self.sio_auto(self.socketIO,'update', {'id': iname, "phase": 1, 'val': -1, 'max': -1})


        # print("{0} start pre".format(args_d['local_id']))
        ret=pre_process.pre_process(
            namedtuple('Struct', args_d.keys())(*args_d.values()))
        self.responseQueue.put({'id':args_d['local_id'],'tensor':ret})
