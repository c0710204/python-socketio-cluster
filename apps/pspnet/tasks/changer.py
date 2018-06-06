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
except Exception as e:
    print(__file__,e)
    from . import task 

class changer(task):
    
    handler_type = "Process"
    handle = ""
    mainthread = False
    def __init__(self,**kwargs):
        self.dict=kwargs
    def uptime(self):
        return self.upcount.value
    def prepare(self):
        task.prepare(self)
    def deploy(self):
        pass
        
    def ask_and_wait(self, args_d):
        self.upcount.value+=1
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
        self.upcount.value-=1
        return ret['tensor']

    def run(self, args_s):
        # print("\nThread info : {0} => func {1}".format(multiprocessing.current_process().name,__file__))
        args_d = json.loads(args_s)
        for k in self.dict:
            args_d[k]=self.dict[k]
        self.responseQueue.put({'id':args_d['local_id'],'tensor':args_d})
