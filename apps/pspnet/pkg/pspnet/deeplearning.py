
from __future__ import print_function
from __future__ import division
from os.path import splitext, join, isfile
from os import environ
import os
from math import ceil
import argparse
import numpy as np
from scipy import misc, ndimage
from keras.backend.tensorflow_backend import set_session
from keras import backend as K
from psp_tf.pspnet import *
import tensorflow as tf
import uuid
import cPickle as pkl
from socketIO_client import SocketIO, LoggingNamespace
pspnet_keep=None

def sio_auto(sio,a,b):
        if sio is None:
            return
        try:
            sio.emit(a,b)
            #sio.wait(seconds=1)
        except Exception as e:
            print(e)
def deep_process(args):
    global pspnet_keep
    from os import listdir
    from os.path import isfile, join

    onlyfiles = [f for f in listdir(args.input_path) if isfile(join(args.input_path, f))]
    import tqdm
    batch_size=16
    #***************************
    if (args.sess):
      print('try to use exists sess...')
      sess=args.sess
    else:
      config = tf.ConfigProto()
      #config.gpu_options.allow_growth = True
      #config.gpu_options.per_process_gpu_memory_fraction = 0.4
      sess = tf.Session(config=config)
      set_session(sess)

  #***************************
    if args.model_ok:
        pspnet=args.model_ok
    else:
        if "pspnet50" in args.model:
            pspnet = PSPNet50(nb_classes=150, input_shape=(473, 473),
                            weights=args.model)
        else:
            print("Network architecture not implemented.")
    print('try to use exists sess... success')
    if args.multi_scale:
      EVALUATION_SCALES = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75]  # must be all floats!
      #EVALUATION_SCALES = [0.15, 0.25, 0.5]  # must be all floats!

    #print ("memory cost of model={0}\n".format(sess.run(tf.contrib.memory_stats.BytesInUse())))
    cache=[]
    image_cache=[]
    ind=0
    metadata=[]


    input_tensor=args.input
    
    data_npy=np.load(input_tensor['npy'])

    with open(input_tensor['pkl']) as f:
        metadata = pkl.load(f)
    filename, ext = splitext(input_tensor['npy'])
    panid=os.path.basename(filename)


    padded_prediction=np.zeros(data_npy.shape[:-1]+(150,))
    print("{0} load ok...\n".format(input_tensor['npy']))
    #sio_auto(args.socketIO,'update',{'id':iname,"phase":2,'val':0,'max':len(onlyfiles)})
    for i_start in tqdm.trange(0,len(metadata),batch_size):
        i_end=i_start+batch_size
        if i_end>len(metadata):
            i_end=len(metadata)
        padded_prediction[i_start:i_end]=pspnet.predict(data_npy[i_start:i_end],  args.flip)

    package={}
    
    for e in tqdm.tqdm(EVALUATION_SCALES):
        index_list=[x for x,y in zip(range(len(metadata)),metadata) if y['scale']==e]
        metadata_e=[y for x,y in zip(range(len(metadata)),metadata) if y['scale']==e]
        p_npy="{0}/{1}_{2}.npy".format(args.output_path,panid,e)
        p_pkl="{0}/{1}_{2}.pkl".format(args.output_path,panid,e)
        package['{0}'.format(e)]={'pkl':p_pkl,'npy':p_npy}
        print(index_list)
        np.save(p_npy,padded_prediction[np.array(index_list)])
        with open(p_pkl, "wb") as f:
            pkl.dump(metadata_e, f)
    #package={'pkl':"{0}/_{1}_metadata.pkl".format(args.output_path,panid),'npy':"{0}/_{1}_data.npy".format(args.output_path,panid)}

    os.remove(input_tensor['npy'])
    os.remove(input_tensor['pkl'])

    return package

    # for fpath in trange(len(metadata)):
    #   #read
    #   ind+=1
    #   padded_img=data_npy[ind]
    #   cache.append((scale,y1,y2,x1,x2,fpath,iname))
    #   image_cache.append(padded_img)
    #   #run
    #   if len(cache)<batch_size:
    #     continue
    #   #print("dispath..")
    #   padded_prediction=pspnet.predict(np.array(image_cache),  args.flip)
    #   iname=""
    #   for i in range(len(cache)):
    #     scale,y1,y2,x1,x2,fpath,iname=cache[i]
    #     prediction = padded_prediction[i,0:y2-y1, 0:x2-x1, :]
    #     np.save(args.output_path+'/'+fpath,prediction)
    #   #sio_auto(args.socketIO,'update',{'id':iname,"phase":2,'val':ind,'max':len(onlyfiles)})
    #   #args.socketIO.wait(seconds=1)
    #   cache=[]
    #   image_cache=[]
    #   padded_prediction=[]
    # for fpath in onlyfiles:
    #     try:
    #         os.remove(args.input_path+'/'+fpath)
    #     except Exception as e:
    #             pass
    #     pass
    # if len(image_cache)>0:
    #     padded_prediction=pspnet.predict(np.array(image_cache),  args.flip)
    #     for i in range(len(cache)):
    #       scale,y1,y2,x1,x2,fpath,iname=cache[i]
    #       prediction = padded_prediction[i,0:y2-y1, 0:x2-x1, :]
    #       np.save(args.output_path+'/'+fpath,prediction)
    #     cache=[]
    #     image_cache=[]
    #     filename=fpath.split('_-123-_')
    #     #sio_auto(args.socketIO,'update',{'id':iname,"phase":2,'val':ind,'max':len(onlyfiles)})
    #     #args.socketIO.wait(seconds=1)

if __name__=='__main__':

  remote_uuid="{0}{1}".format(uuid.uuid4(),"_deeplearning")
  socketIO=SocketIO('localhost', 30091, LoggingNamespace)
  parser = argparse.ArgumentParser()
  parser.add_argument('-m', '--model', type=str, default='pspnet50_ade20k',
                      help='Model/Weights to use',
                      choices=['pspnet50_ade20k',
                               'pspnet101_cityscapes',
                               'pspnet101_voc2012'])
  parser.add_argument('-i', '--input_path', type=str, default='p1/',
                      help='Path the input image')
  parser.add_argument('-o', '--output_path', type=str, default='p2/',
                      help='Path to output')
  parser.add_argument('--id', default="0")
  parser.add_argument('-s', '--sliding', action='store_true',
                      help="Whether the network should be slided over the original image for prediction.")
  parser.add_argument('-f', '--flip', action='store_true',
                      help="Whether the network should predict on both image and flipped image.")
  parser.add_argument('-ms', '--multi_scale', action='store_true',
                      help="Whether the network should predict on multiple scales.")
  args = parser.parse_args()
  args.remote_uuid=remote_uuid
  args.socketIO=socketIO
  deep_process(args)
