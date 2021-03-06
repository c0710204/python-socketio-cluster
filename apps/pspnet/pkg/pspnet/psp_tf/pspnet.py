#!/usr/bin/env python
"""
This module is a Keras/Tensorflow based implementation of Pyramid Scene Parsing Networks.

Original paper & code published by Hengshuang Zhao et al. (2017)
"""
from __future__ import print_function
from __future__ import division
from os.path import splitext, join, isfile,realpath,split
from os import environ
from math import ceil
import argparse
import numpy as np
from scipy import misc, ndimage
from keras.backend.tensorflow_backend import set_session
from keras import backend as K
import sys
import keras
from keras.models import model_from_json,Model
import tensorflow as tf
import layers_builder as layers
import utils
import time
from tqdm import *

#from keras.backend.tensorflow_backend import set_session
#config = tf.ConfigProto()
#config.gpu_options.per_process_gpu_memory_fraction = 0.3

__author__ = "Vlad Kryvoruchko, Chaoyue Wang, Jeffrey Hu & Julian Tatsch"


# These are the means for the ImageNet pretrained ResNet
DATA_MEAN = np.array([[[123.68, 116.779, 103.939]]])  # RGB order
EVALUATION_SCALES = [1.0]  # must be all floats!
GPU_timer = 0
GPU_count = 0


class PSPNet(object):
    """Pyramid Scene Parsing Network by Hengshuang Zhao et al 2017."""

    def __init__(self, nb_classes, resnet_layers, input_shape, weights,path="./weights"):
        """Instanciate a PSPNet."""
        self.input_shape = input_shape
        path=realpath(split(realpath(__file__))[0]+"/../weights/")
        print(path)
        sys.stdout.flush()
        print("build extra model for speedup")

        inp=K.placeholder(shape=(None,473, 473,150),name='a')
        inp2=K.placeholder(shape=(None,473, 473,150),name='a_flip')
        inp_flip=K.reverse(inp2,axes=2)
        cmb=(inp+inp_flip)/2
        self.M_comb=[cmb,inp,inp2]

        json_path = join(path, "keras", weights + ".json")
        h5_path = join(path, "keras", weights + ".h5")
        if isfile(json_path) and isfile(h5_path):
            print("Keras model & weights found, loading...")
            with open(json_path, 'r') as file_handle:
                self.model = model_from_json(file_handle.read())
            
        

            # layer_flip = keras.layers.Lambda(lambda x: K.reverse(x,axes=2),name="extened_lda_rev")
            # # layer_split_1=keras.layers.Lambda(lambda x: K.slice(x, [0,0,0,0], [K.shape(x)[0]/2,K.shape(x)[1],K.shape(x)[2],K.shape(x)[3]]))
            # # layer_split_2=keras.layers.Lambda(lambda x: K.slice(x, [K.shape(x)[0]/2,0,0,0], [K.shape(x)[0]/2,K.shape(x)[1],K.shape(x)[2],K.shape(x)[3]]))

            # layer_split_1= keras.layers.Lambda(lambda x: x[:K.shape(x)[0]//2,:,:,:], output_shape=lambda x:x ,name="extened_lda_s1")
            # layer_split_2= keras.layers.Lambda(lambda x: x[K.shape(x)[0]//2:,:,:,:], output_shape=lambda x:x ,name="extened_lda_s2")
            # layer_dev=keras.layers.Lambda(lambda x: x/2, output_shape=lambda x:x,name="extened_lda_dev" )
            # model_in=self.model.get_layer(name="input_1").input
            # model_out=self.model.get_layer(name="activation_58").output

            # model_out_normal=layer_split_1(model_out)
            # model_out_flip=layer_flip(layer_split_2(model_out))
            # cmb_0=keras.layers.Add(name="extened_add")([model_out_normal,model_out_flip])
            # cmb=layer_dev(cmb_0)
            # self.model=Model(model_in,cmb)
            self.model.load_weights(h5_path)
            print("Keras model & weights found, loaded success")
        else:
            print("No Keras model & weights found, import from npy weights.")
            self.model = layers.build_pspnet(nb_classes=nb_classes,
                                             resnet_layers=resnet_layers,
                                             input_shape=self.input_shape)

            self.set_npy_weights(weights)
        


    def predict(self, img, flip_evaluation,sess=None):
        """
        Predict segementation for an image.

        Arguments:
            img: must be rowsxcolsx3
        """
        #global GPU_timer
        global GPU_count
        import time
        h_ori, w_ori = img.shape[1:3]
        if img.shape[1:3] != self.input_shape:
            print("Input %s not fitting for network size %s, resizing. You may want to try sliding prediction for better results." % (
                img.shape[0:2], self.input_shape))
                
            img = misc.imresize(img, self.input_shape)
        ts=time.time()
        float_img = img.astype('float16')
        # print('-------------------------------------------------------')
        # print(time.time()-ts)
        centered_image = float_img - DATA_MEAN
        # print(time.time()-ts)
        bgr_image = centered_image[:, :, :, ::-1]  # RGB => BGR
        # print(time.time()-ts)
        input_data = bgr_image


        # utils.debug(self.model, input_data)
        import time
        GPU_timer=0
        
        #print("start gpu")
        #try:
        # print(time.time()-ts)
        input_data_x=np.concatenate((input_data,np.flip(input_data, axis=2)), axis=0)
        GPU_timer -= time.time()
        all_prediction = self.model.predict(input_data_x)
        GPU_timer += time.time()

        x=np.array_split(all_prediction, 2)
        regular_prediction=x[0]
        flipped_prediction=x[1]
        GPU_timer -= time.time()

        sess=K.get_session()
        prediction=sess.run(self.M_comb[0],feed_dict={self.M_comb[1]:regular_prediction,self.M_comb[2]:flipped_prediction})
        
        
        GPU_timer += time.time()
        #prediction=all_prediction
        #flipped_prediction=np.flip(flipped_prediction, axis=2)
        #prediction = (regular_prediction + flipped_prediction) / 2.0
        # # print(time.time()-ts)
        # #except  e:
        # #    print(e)
        # #print("end gpu")
        
        # GPU_count += 1
        # if flip_evaluation:
        #     #print("Predict flipped")
        #     GPU_timer -= time.time()

        #     flipped_prediction = np.flip(self.model.predict(np.flip(input_data, axis=2)), axis=2)
        #     # print(time.time()-ts)
        #     GPU_timer += time.time()
        #     GPU_count += 1
        #     prediction = (regular_prediction + flipped_prediction) / 2.0
        #     # print(time.time()-ts)
        # else:
        #     prediction = regular_prediction
        # print(time.time()-ts)
        if img.shape[1:3] != self.input_shape:  # upscale prediction if necessary
            h, w = prediction.shape[1:3]
            print("upscale triggered!")
            prediction = ndimage.zoom(prediction, (1, 1.*h_ori/h, 1.*w_ori/w, 1.),
                                      order=1, prefilter=False)
        # print(time.time()-ts)
        return prediction,GPU_timer

    def preprocess_image(self, img):
        """Preprocess an image as input."""

        return input_data

    def set_npy_weights(self, weights_path):
        """Set weights from the intermediary npy file."""
        npy_weights_path = join("weights", "npy", weights_path + ".npy")
        json_path = join("weights", "keras", weights_path + ".json")
        h5_path = join("weights", "keras", weights_path + ".h5")

        print("Importing weights from %s" % npy_weights_path)
        weights = np.load(npy_weights_path, encoding="latin1").item()

        whitelist = ["InputLayer", "Activation", "ZeroPadding2D", "Add",
                     "MaxPooling2D", "AveragePooling2D", "Lambda", "Concatenate", "Dropout"]

        weights_set = 0
        for layer in self.model.layers:
            #print("Processing %s" % layer.name)
            if layer.name[:4] == 'conv' and layer.name[-2:] == 'bn':
                mean = weights[layer.name]['mean'].reshape(-1)
                variance = weights[layer.name]['variance'].reshape(-1)
                scale = weights[layer.name]['scale'].reshape(-1)
                offset = weights[layer.name]['offset'].reshape(-1)

                self.model.get_layer(layer.name).set_weights([mean, variance,
                                                              scale, offset])
                weights_set += 1
            elif layer.name[:4] == 'conv' and not layer.name[-4:] == 'relu':
                try:
                    weight = weights[layer.name]['weights']
                    self.model.get_layer(layer.name).set_weights([weight])
                except Exception:
                    biases = weights[layer.name]['biases']
                    self.model.get_layer(layer.name).set_weights([weight,
                                                                  biases])
                weights_set += 1
            elif layer.__class__.__name__ in whitelist:
                # print("Nothing to set in %s" % layer.__class__.__name__)
                pass
            else:
                print("Warning: Did not find weights for keras layer %s in numpy weights" % layer)

        print("Set a total of %i weights" % weights_set)

        print('Finished importing weights.')

        print("Writing keras model & weights")
        json_string = self.model.to_json()
        with open(json_path, 'w') as file_handle:
            file_handle.write(json_string)
        self.model.save_weights(h5_path)
        print("Finished writing Keras model & weights")


class PSPNet50(PSPNet):
    """Build a PSPNet based on a 50-Layer ResNet."""

    def __init__(self, nb_classes, weights, input_shape,path="./weights"):
        """Instanciate a PSPNet50."""
        PSPNet.__init__(self, nb_classes=nb_classes, resnet_layers=50,
                        input_shape=input_shape, weights=weights,path=path)


class PSPNet101(PSPNet):
    """Build a PSPNet based on a 101-Layer ResNet."""

    def __init__(self, nb_classes, weights, input_shape):
        """Instanciate a PSPNet101."""
        PSPNet.__init__(self, nb_classes=nb_classes, resnet_layers=101,
                        input_shape=input_shape, weights=weights)


def pad_image(img, target_size):
    """Pad an image up to the target size."""
    rows_missing = target_size[0] - img.shape[0]
    cols_missing = target_size[1] - img.shape[1]
    padded_img = np.pad(img, ((0, rows_missing), (0, cols_missing), (0, 0)), 'constant')
    return padded_img


def visualize_prediction(prediction):
    """Visualize prediction."""
    cm = np.argmax(prediction, axis=2) + 1
    color_cm = utils.add_color(cm)
    plt.imshow(color_cm)
    plt.show()


def predict_sliding(full_image, net, flip_evaluation):
    """Predict on tiles of exactly the network input shape so nothing gets squeezed."""
    tile_size = net.input_shape
    classes = net.model.outputs[0].shape[3]
    overlap = 1/3

    stride = ceil(tile_size[0] * (1 - overlap))
    # strided convolution formula
    tile_rows = int(ceil((full_image.shape[0] - tile_size[0]) / stride) + 1)
    tile_cols = int(ceil((full_image.shape[1] - tile_size[1]) / stride) + 1)
    #print("Need %i x %i prediction tiles @ stride %i px" % (tile_cols, tile_rows, stride))
    full_probs = np.zeros((full_image.shape[0], full_image.shape[1], classes))
    count_predictions = np.zeros((full_image.shape[0], full_image.shape[1], classes))
    tile_counter = 0
    with trange(tile_rows*tile_cols) as pbar:
        for rc in pbar:
            row = int(rc/tile_cols)
            col = rc % tile_cols
            x1 = int(col * stride)
            y1 = int(row * stride)
            x2 = min(x1 + tile_size[1], full_image.shape[1])
            y2 = min(y1 + tile_size[0], full_image.shape[0])
            x1 = max(int(x2 - tile_size[1]), 0)  # for portrait images the x1 underflows sometimes
            y1 = max(int(y2 - tile_size[0]), 0)  # for very few rows y1 underflows

            img = full_image[y1:y2, x1:x2]
            padded_img = pad_image(img, tile_size)
            # plt.imshow(padded_img)
            # plt.show()
            tile_counter += 1
            pbar.set_description("Predicting tile {0}-{1}".format(row, col))
            padded_prediction = net.predict(padded_img, flip_evaluation)
            prediction = padded_prediction[0:img.shape[0], 0:img.shape[1], :]
            count_predictions[y1:y2, x1:x2] += 1
            # accumulate the predictions also in the overlapping regions
            full_probs[y1:y2, x1:x2] += prediction
            del prediction
            del padded_prediction
            del padded_img
    # average the predictions in the overlappi ng regions
    full_probs /= count_predictions
    # visualize normalization Weights
    # plt.imshow(np.mean(count_predictions, axis=2))
    # plt.show()
    return full_probs


def predict_multi_scale(full_image, net, scales, sliding_evaluation, flip_evaluation):
    """Predict an image by looking at it with different scales."""
    classes = net.model.outputs[0].shape[3]
    full_probs = np.zeros((full_image.shape[0], full_image.shape[1], classes))
    h_ori, w_ori = full_image.shape[:2]
    with tqdm(scales) as pbar:
        for scale in pbar:
            pbar.set_description("Predicting image scaled by %f" % scale)
            scaled_img = misc.imresize(full_image, size=scale, interp="bilinear")
            if sliding_evaluation:
                scaled_probs = predict_sliding(scaled_img, net, flip_evaluation)
            else:
                scaled_probs = net.predict(scaled_img, flip_evaluation)
            # scale probs up to full size
            h, w = scaled_probs.shape[:2]
            probs = ndimage.zoom(scaled_probs, (1.*h_ori/h, 1.*w_ori/w, 1.),
                                 order=1, prefilter=False)
            # visualize_prediction(probs)
            # integrate probs over all scales
            full_probs += probs
    full_probs /= len(scales)
    return full_probs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, default='pspnet50_ade20k',
                        help='Model/Weights to use',
                        choices=['pspnet50_ade20k',
                                 'pspnet101_cityscapes',
                                 'pspnet101_voc2012'])
    parser.add_argument('-i', '--input_path', type=str, default='example_images/ade20k.jpg',
                        help='Path the input image')
    parser.add_argument('-o', '--output_path', type=str, default='example_results/ade20k.jpg',
                        help='Path to output')
    parser.add_argument('--id', default="0")
    parser.add_argument('-s', '--sliding', action='store_true',
                        help="Whether the network should be slided over the original image for prediction.")
    parser.add_argument('-f', '--flip', action='store_true',
                        help="Whether the network should predict on both image and flipped image.")
    parser.add_argument('-ms', '--multi_scale', action='store_true',
                        help="Whether the network should predict on multiple scales.")
    args = parser.parse_args()

    environ["CUDA_VISIBLE_DEVICES"] = args.id

    config = tf.ConfigProto()
    #config.gpu_options.allow_growth = True
    #config.gpu_options.per_process_gpu_memory_fraction = 0.4
    sess = tf.Session(config=config)
    set_session(sess)

    with sess:
        img = misc.imread(args.input_path)
        img = misc.imresize(img, 10)
        print(args)

        if "pspnet50" in args.model:
            pspnet = PSPNet50(nb_classes=150, input_shape=(473, 473),
                              weights=args.model)
        elif "pspnet101" in args.model:
            if "cityscapes" in args.model:
                pspnet = PSPNet101(nb_classes=19, input_shape=(713, 713),
                                   weights=args.model)
            if "voc2012" in args.model:
                pspnet = PSPNet101(nb_classes=21, input_shape=(473, 473),
                                   weights=args.model)

        else:
            print("Network architecture not implemented.")

        if args.multi_scale:
            EVALUATION_SCALES = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75]  # must be all floats!
            # EVALUATION_SCALES = [0.15, 0.25, 0.5]  # must be all floats!
        # fit test:

        import time
        t = time.time()
        class_scores = predict_multi_scale(img, pspnet, EVALUATION_SCALES, args.sliding, args.flip)
        t = time.time()-t
        print("Writing results...")

        class_image = np.argmax(class_scores, axis=2)
        #pm = np.max(class_scores, axis=2)
        #colored_class_image = utils.color_class_image(class_image, args.model)
        # colored_class_image is [0.0-1.0] img is [0-255]
        #alpha_blended = 0.5 * colored_class_image + 0.5 * img
        filename, ext = splitext(args.output_path)
        np.save(filename+".npy", class_scores)
        #misc.imsave(filename + "_seg" + ext, colored_class_image)
        #misc.imsave(filename + "_probs" + ext, pm)
        #misc.imsave(filename + "_seg_blended" + ext, alpha_blended)
        # visualize_prediction(class_scores)
        l = [np.count_nonzero(class_image == i) for i in range(150)]
        l = np.array(l).astype(np.float)/(img.shape[0]*img.shape[1])
        with open("treecount2.txt", 'a+') as f:
            f.write("{0} {1}\n".format(filename, ','.join(map(str, l))))
        with open("GPUtime2.txt", 'a+') as f:
            f.write("{0} {1} {2} {3}\n".format(filename, GPU_timer, t, GPU_count))
