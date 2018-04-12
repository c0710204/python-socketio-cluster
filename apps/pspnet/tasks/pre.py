from __future__ import print_function
from __future__ import division
from task import task
import time
import numpy as np
from scipy import misc, ndimage
from ..pkg.pspnet import pre_process
from collections import namedtuple
from ..pkg.pspnet import utils
import uuid
import multiprocessing
import logging
import sys
import json
class pre(task):

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
        iname = args_d['panid']
        self.socketIO.emit('update', {'id': iname, "phase": 1, 'val': -1, 'max': -1})
        self.socketIO.wait(seconds=1)
        print("{0} start pre".format(args_d['local_id']))
        pre_process.pre_process(
            namedtuple('Struct', args_d.keys())(*args_d.values()))
