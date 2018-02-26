from __future__ import print_function
from __future__ import division
from tqdm import tqdm,trange
import argparse
import numpy as np
from scipy import misc, ndimage
import multiprocessing as mp
#import uuid
#remote_uuid=uuid.uuid4()
#from socketIO_client import SocketIO, LoggingNamespace
#socketIO=SocketIO('localhost', 30001, LoggingNamespace)
from math import ceil
def pad_image(img, target_size):
    """Pad an image up to the target size."""
    rows_missing = target_size[0] - img.shape[0]
    cols_missing = target_size[1] - img.shape[1]
    padded_img = np.pad(img, ((0, rows_missing), (0, cols_missing), (0, 0)), 'constant')
    return padded_img


def predict_sliding(funchandler,full_image, net, flip_evaluation,scale):

  """Predict on tiles of exactly the network input shape so nothing gets squeezed."""
  tile_size = net['input_shape']
  classes = net['model.outputs[0].shape[3]']
  overlap = 1/3
  stride = ceil(tile_size[0] * (1 - overlap))
  tile_rows = int(ceil((full_image.shape[0] - tile_size[0]) / stride) + 1)  # strided convolution formula
  tile_cols = int(ceil((full_image.shape[1] - tile_size[1]) / stride) + 1)
  #print("Need %i x %i prediction tiles @ stride %i px" % (tile_cols, tile_rows, stride))
  tile_counter = 0
  with trange(tile_rows*tile_cols) as pbar:
    for rc in pbar:
      row=int(rc/tile_cols)
      col=rc%tile_cols
      x1 = int(col * stride)
      y1 = int(row * stride)
      x2 = min(x1 + tile_size[1], full_image.shape[1])
      y2 = min(y1 + tile_size[0], full_image.shape[0])
      x1 = max(int(x2 - tile_size[1]), 0)  # for portrait images the x1 underflows sometimes
      y1 = max(int(y2 - tile_size[0]), 0)  # for very few rows y1 underflows
      img = full_image[y1:y2, x1:x2]
      padded_img = pad_image(img, tile_size)
      tile_counter += 1
      #socketIO.emit('update',{id:remote_uuid,val:rc,max:tile_rows*tile_cols})
      #socketIO.wait(seconds=1)
      pbar.set_description("Predicting tile {0}-{1}".format(row,col))
      funchandler((padded_img, flip_evaluation,y1,y2,x1,x2,scale))
  return 0


def predict_multi_scale(funchandler,full_image, net, scales, sliding_evaluation, flip_evaluation):
  """Predict an image by looking at it with different scales."""
  classes = net['model.outputs[0].shape[3]']
  full_probs = np.zeros((full_image.shape[0], full_image.shape[1], classes))
  h_ori, w_ori = full_image.shape[:2]
  with tqdm(scales) as pbar:
    for scale in pbar:
        pbar.set_description("Predicting image scaled by %f" % scale)
        scaled_img = misc.imresize(full_image, size=scale, interp="bilinear")
        if sliding_evaluation:
            predict_sliding(funchandler,scaled_img, net, flip_evaluation,scale)
        else:
            funchandler((scaled_img, flip_evaluation))
  return 0
