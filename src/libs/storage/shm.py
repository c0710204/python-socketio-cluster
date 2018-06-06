import multiprocessing
import sys
from os.path import splitext, join, isfile, basename
from os import environ
from math import ceil
import subprocess
import logging
import json
import time
import random
import numpy
import cPickle as pkl
import platform

class shm_obj(object):
    def __init__(self,manager):
        self.manager=manager
        self.label=""
        self.shm_file=""
        self.meta={}
        self.status="Alloc"
    def save(self):
        raise NotImplemented
    def load(self):
        raise NotImplemented
    def release(self):
        self.manager.release(self.label)
class shm_npy(shm_obj):        
    def base(original_obj):
        s=shm_npy(original_obj.manager)
        s.label=original_obj.label
        s.shm_file=original_obj.shm_file
        s.meta=original_obj.meta
        s.status=original_obj.status
        return s
    def save(self,ndarr):
        if self.status=="init":
            np.save(self.shm_file,ndarr)
            self.status="ready"
        else:
            raise IOError("shm not inited")
    def load(self):
        if self.status=="ready"
            return np.load(self.shm_file)
        else:
            raise IOError("shm not ready")
        
class tensor(object):
    def __init__(self,manager,data,mete):
        self.data=shm_npy.base(manager.alloc())
        self.meta=

class shm(object):

    def __init__(self):
        # check platform - only support linux, others will use local as storage
        if platform.system()=="Linux":
            self.shmroot="/dev/shm/"
        else:
            print("[WARNING]System do not support shared memory, using local temp folder instead!")
            self.shmroot="./tmp/"
            os.mkdir(self.shmroot)
        self.personal_name="{0:10}/".format( random.randint(1, 100000000))
        self.storage_root=self.shmroot+self.personal_name
        os.mkdir(self.storage_root)
        #init manager
        self.manager=multiprocessing.Manager()
        self.info_list=manager.dict()   
    def obj_alloc(self,obj)
        
    
    def alloc(self,name=None):
        if name == None:
            name="localfile{0:10}".format( random.randint(1, 100000000))
        local=shm_obj(self)
        local.shm_file="{0}{1}".format(self.storage_root,name)
        local.label=name
        local.status="init"
        self.info_list[name]=local
        return local

    def save():
        raise NotImplemented
    def load():
        raise NotImplemented
        


