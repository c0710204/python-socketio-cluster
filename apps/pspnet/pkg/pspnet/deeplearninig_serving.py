
from __future__ import print_function
from __future__ import division
from os.path import splitext, join, isfile
from os import environ
from math import ceil
import argparse
import numpy as np
from scipy import misc, ndimage
from keras.backend.tensorflow_backend import set_session  
from keras import backend as K
from psp_tf.pspnet import *
import tensorflow as tf
import uuid
from socketIO_client import SocketIO, LoggingNamespace,BaseNamespace

config = tf.ConfigProto()
#config.gpu_options.allow_growth = True
#config.gpu_options.per_process_gpu_memory_fraction = 0.4
sess = tf.Session(config=config)
set_session(sess)
batch_size=1
args_flip=True
#***************************
with sess:
  pspnet = PSPNet50(nb_classes=150, input_shape=(473, 473),weights=args.model)
  EVALUATION_SCALES = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75] 
  class deep_Namespace(BaseNamespace):
    def on_request(self,*args):
      fpath=args[0]['fpath']
      padded_img=np.load(fpath)
      iname,scale,y1,y2,x1,x2,_=fpath.split('_-_')
      y1=int(y1)
      y2=int(y2)
      x1=int(x1)
      x2=int(x2)
      cache.append((scale,y1,y2,x1,x2,fpath,iname))
      image_cache.append(padded_img)
      #run
      if args[0]['batched'] and len(cache)<batch_size:
        return {'status':'batched'}

      padded_prediction=pspnet.predict(np.array(image_cache),  args_flip)
      iname=""
      for i in range(len(cache)):
        scale,y1,y2,x1,x2,fpath,iname=cache[i]
        prediction = padded_prediction[i,0:y2-y1, 0:x2-x1, :]
        np.save(fpath+".out",prediction)
      args.socketIO.emit('update',{'id':iname,"phase":2,'val':ind,'max':len(onlyfiles)})
      args.socketIO.wait(seconds=1)
      ret={'status':"done",'list':cache}
      cache=[]
      image_cache=[]
      padded_prediction=[]
      return ret
if __name__=='__main__':
  #receive request from socketio
  deep_process(args)