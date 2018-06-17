from __future__ import print_function
from __future__ import division
import sys

sys.path.append('.')
sys.path.append('..')
import time
import numpy as np
from scipy import misc, ndimage

from collections import namedtuple
from pkg.pspnet import utils
import uuid
import multiprocessing
import logging
import json

#'130083', 'dHMpdTDus3k9Ywcxin5Z-g', '/scratch/guxi/googlestreeview_download/temp/DownloadedImages/dHMpdTDus3k9Ywcxin5Z-g.jpg', '/scratch/guxi/googlestreeview_download/result/'

iname="J1RW1BZwFAhymbfMdxE6Mw"

img = misc.imread('/scratch/guxi/googlestreeview_download/temp/DownloadedImages/{0}.jpg'.format(iname))
class_image=np.load("/scratch/guxi/googlestreeview_download/result/{0}.npy".format(iname))
#img = misc.imresize(img, 10)

colored_class_image = utils.color_class_image(class_image,
                                              'pspnet50_ade20k')
#colored_class_image is [0.0-1.0] img is [0-255]
alpha_blended = 0.9 * colored_class_image + 0.1 * img
misc.imsave("./blended.jpg", alpha_blended)