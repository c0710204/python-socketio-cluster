import argparse
import numpy as np
from scipy import misc, ndimage
try:
    from scipy.misc import imread 
except:
    from imageio import imread
import img_combine_func2
from os.path import splitext, join, isfile, basename
import utils
from socketIO_client import SocketIO, LoggingNamespace
import uuid


def img_combine2(args):
    if args.multi_scale:
        EVALUATION_SCALES = [0.5, 0.75, 1.0, 1.25, 1.5,
                             1.75]  # must be all floats!
        #EVALUATION_SCALES = [0.15, 0.25, 0.5]  # must be all floats!
    #fit test:
    EVALUATION_SCALES.reverse()
    img = misc.imread(args.input_path)
    #img = misc.imresize(img, 10)
    img_shape = img.shape
    pspnet = {}
    pspnet['input_shape'] = (473, 473)
    pspnet['model.outputs[0].shape[3]'] = 150
    funchandler=None
    return img_combine_func2.predict_multi_scale(funchandler, img_shape,
                                                 pspnet, EVALUATION_SCALES,
                                                 args.sliding, args.flip, args)


