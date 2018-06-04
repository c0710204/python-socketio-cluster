
import argparse
import numpy as np
from scipy import misc, ndimage
try:
    from pre_process_func import predict_multi_scale
except:
    from .pre_process_func import predict_multi_scale
from os.path import splitext, join, isfile,basename
from socketIO_client import SocketIO, LoggingNamespace
import uuid
import cPickle as pkl
def pre_process(args):
  if args.multi_scale:
      EVALUATION_SCALES = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75]  # must be all floats!
      #EVALUATION_SCALES = [0.15, 0.25, 0.5]  # must be all floats!
  #fit test:
  img = misc.imread(args.input_path)
  #img = misc.imresize(img, 10)
  pspnet={}
  pspnet['input_shape']=(473, 473)
  pspnet['model.outputs[0].shape[3]']=150
  res_metadata=[]
  res_data=[]
  def funchandler(inp,img):
    res_metadata.append(inp)
    res_data.append(img)
      
  class_scores = predict_multi_scale(funchandler, img, pspnet, EVALUATION_SCALES, args.sliding, args.flip)

  filename, ext = splitext(args.output_path)
  pkl_name="{0}.pkl".format(filename)
  npy_name="{0}.npy".format(filename)
  
  with open(pkl_name, "wb") as f:
    pkl.dump(res_metadata, f)
  np.save(npy_name,np.array(res_data))
  return {"pkl":pkl_name,'npy':npy_name}

if __name__=='__main__':
  remote_uuid="{0}{1}".format(uuid.uuid4(),"_imagecombine")
  socketIO=SocketIO('localhost', 30091, LoggingNamespace)
  parser = argparse.ArgumentParser()
  parser.add_argument('-m', '--model', type=str, default='pspnet50_ade20k',
                      help='Model/Weights to use',
                      choices=['pspnet50_ade20k',
                               'pspnet101_cityscapes',
                               'pspnet101_voc2012'])
  parser.add_argument('-i', '--input_path', type=str, default='example_images/ade20k.jpg',
                      help='Path the input image')
  parser.add_argument('-o', '--output_path', type=str, default='p1/',
                      help='Path to output')
  parser.add_argument('--id', default="0")
  parser.add_argument('-s', '--sliding', action='store_true',
                      help="Whether the network should be slided over the original image for prediction.")
  parser.add_argument('-f', '--flip', action='store_true',
                      help="Whether the network should predict on both image and flipped image.")
  parser.add_argument('-ms', '--multi_scale', action='store_true',
                      help="Whether the network should predict on multiple scales.")
  args = parser.parse_args()
  filename, ext = splitext(args.output_path)
  iname = basename(filename)
  socketIO.emit('update',{'id':iname,"phase":1,'val':-1,'max':-1})
  socketIO.wait(seconds=1)
  pre_process(args)
  socketIO.emit('update',{'id':iname,"phase":1,'val':1,'max':1})
  socketIO.wait(seconds=1)
