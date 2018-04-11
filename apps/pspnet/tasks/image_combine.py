from __future__ import print_function
from __future__ import division
from task import task
import time
import numpy as np
from scipy import misc, ndimage
from ..pkg.pspnet import img_combine2
from ..pkg.pspnet.psp_tf.pspnet import PSPNet50
from collections import namedtuple
from ..pkg.pspnet import utils
import uuid
import multiprocessing
import logging
import json
import sys
class image_combine(task):

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
        iname = args_d['panid']
        ext = args_d['ext']
        filename = args_d['filename']
        self.socketIO.emit('update', {'id': iname, "phase": 3, 'val': -1, 'max': -1})
        self.socketIO.wait(seconds=1)
        class_scores = img_combine2.img_combine2(
            namedtuple('Struct', args_d.keys())(*args_d.values()))

        print("blended...")
        img = misc.imread("./{0}{1}".format(panid, ext))
        # img = misc.imresize(img, 10)

        class_image = np.argmax(class_scores, axis=2)
        np.save("{0}.npy".format(panid),class_image)
        l = [np.count_nonzero(class_image == i) for i in range(150)]
        np.save("{0}_classify.npy".format(panid),l)

        # pm = np.max(class_scores, axis=2)
        # colored_class_image = utils.color_class_image(class_image,
        #                                               args_d['model'])
        #colored_class_image is [0.0-1.0] img is [0-255]
        # alpha_blended = 0.5 * colored_class_image + 0.5 * img
        # misc.imsave(panid + "_seg_blended" + ext, alpha_blended)
        # for filename in tqdm.tqdm(os.listdir('/tmp')):
        #     if filename.endswith(".npy"):
        #         try:
        #             os.remove(filename)
        #         except Exception:
        #             pass
        self.socketIO.emit('update', {'id': iname, "phase": 3, 'val': 1, 'max': 1})
        self.socketIO.wait(seconds=1)
        self.responseQueue.put(args_d['local_id'])
