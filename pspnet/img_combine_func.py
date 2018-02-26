from __future__ import print_function
from __future__ import division
import numpy as np
from tqdm import tqdm,trange
import argparse
from scipy import misc, ndimage
import multiprocessing as mp
from multiprocessing import Pool
from math import ceil
def pad_image(img, target_size):
    """Pad an image up to the target size."""
    rows_missing = target_size[0] - img.shape[0]
    cols_missing = target_size[1] - img.shape[1]
    padded_img = np.pad(img, ((0, rows_missing), (0, cols_missing), (0, 0)), 'constant')
    return padded_img


def predict_sliding(funchandler,full_image_shape, net, flip_evaluation,scale):

  """Predict on tiles of exactly the network input shape so nothing gets squeezed."""
  tile_size = net['input_shape']
  classes = net['model.outputs[0].shape[3]']
  overlap = 1/3
  stride = ceil(tile_size[0] * (1 - overlap))
  tile_rows = int(ceil((full_image_shape[0] - tile_size[0]) / stride) + 1)  # strided convolution formula
  tile_cols = int(ceil((full_image_shape[1] - tile_size[1]) / stride) + 1)
  #print("Need %i x %i prediction tiles @ stride %i px" % (tile_cols, tile_rows, stride))
  full_probs = np.zeros((full_image_shape[0], full_image_shape[1], classes))
  count_predictions = np.zeros((full_image_shape[0], full_image_shape[1], classes))
  tile_counter = 0
  with trange(tile_rows*tile_cols) as pbar:
    for rc in pbar:
      row=int(rc/tile_cols)
      col=rc%tile_cols
      x1 = int(col * stride)
      y1 = int(row * stride)
      x2 = min(x1 + tile_size[1], full_image_shape[1])
      y2 = min(y1 + tile_size[0], full_image_shape[0])
      x1 = max(int(x2 - tile_size[1]), 0)  # for portrait images the x1 underflows sometimes
      y1 = max(int(y2 - tile_size[0]), 0)  # for very few rows y1 underflows
      tile_counter += 1
      pbar.set_description("Predicting tile {0}-{1}".format(row,col))
      prediction=funchandler(([], flip_evaluation,y1,y2,x1,x2,scale))
      
      count_predictions[y1:y2, x1:x2] += 1
      full_probs[y1:y2, x1:x2] += prediction  # accumulate the predictions also in the overlapping regions
      del prediction
  full_probs /= count_predictions
  return full_probs

def loc_process(all):
    image_loc,zoom,order, prefilter=all
    return ndimage.zoom(image_loc,zoom,order=order, prefilter=prefilter)






def ndimage_zoom_parallel(image,zoom,order,prefilter):
  """provide paralleled ndimage_zoom
  16 threads: 
  real    1m13.070s
  user    2m30.756s
  sys     0m36.668s
  8 threads
  real    1m15.175s
  user    2m26.204s
  sys     0m32.376s
  original:
  real    1m4.097s
  user    0m54.340s
  sys     0m7.640s
  """
  pool = Pool(processes=8)
  List_image=[image[:,:,x] for x in range(image.shape[2])]
  list_all=[(np.reshape(List_image[i],List_image[i].shape+(-1,)),zoom,order,prefilter) for i in range(len(List_image))]
  
  ret=pool.map(loc_process,list_all)
  pool.close()
  pool.join()
  ret=np.moveaxis(np.array(ret),0,-1)
  ret=ret.reshape(ret.shape[0:-2]+(-1,))
  return ret
def ndimage_zoom_parallel_2(list_all):

  pool = Pool(processes=4)
  ret=pool.map(loc_process,list_all)

  pool.close()
  pool.join()  
  full_probs = np.zeros((full_image_shape[0], full_image_shape[1], classes))
  for probs in ret:
    full_probs += probs
  print(full_probs.shape)
  return full_probs


def predict_multi_scale(funchandler,full_image_shape, net, scales, sliding_evaluation, flip_evaluation):
  """Predict an image by looking at it with different scales."""
  classes = net['model.outputs[0].shape[3]']
  full_probs = np.zeros((full_image_shape[0], full_image_shape[1], classes))
  h_ori, w_ori = full_image_shape[:2]
  with tqdm(scales) as pbar:
    probs=[]
    for scale in pbar:
        pbar.set_description("Predicting image scaled by %f" % scale)
        full_image_shape2 =[int(h_ori*scale), int(w_ori*scale),full_image_shape[2]]
        if sliding_evaluation:
            scaled_probs=predict_sliding(funchandler,full_image_shape2, net, flip_evaluation,scale)
        else:
            scaled_probs=funchandler((scaled_img, flip_evaluation))
        h, w = scaled_probs.shape[:2]

        probs = ndimage.zoom(scaled_probs, (1.*h_ori/h, 1.*w_ori/w, 1.),order=1, prefilter=False)
        #probs=ndimage_zoom_parallel(scaled_probs, (1.*h_ori/h, 1.*w_ori/w, 1.),order=1, prefilter=False)
        #probs.append((scaled_probs, (1.*h_ori/h, 1.*w_ori/w, 1.),1,False))

        # visualize_prediction(probs)
        # integrate probs over all scales
    
    full_probs += probs
    #full_probs=ndimage_zoom_parallel_2(probs)
  full_probs /= len(scales)
  return full_probs
