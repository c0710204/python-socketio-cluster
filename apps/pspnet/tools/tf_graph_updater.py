import tensorflow as tf
import numpy as np
#import PIL.Image as Image
#import cv2
from collections import namedtuple
import sys
sys.path.append('.')
def recognize(pb_file_path):
    with tf.Graph().as_default():
        output_graph_def = tf.GraphDef()

        with open(pb_file_path, "rb") as f:
            output_graph_def.ParseFromString(f.read())
            tensors = tf.import_graph_def(output_graph_def, name="")
            print tensors

        with tf.Session() as sess:
            init = tf.global_variables_initializer()
            sess.run(init)

            op = sess.graph.get_operations()

            op_f=None
            for m in op:
                if m.name=="conv1_1_3x3_s2/convolution":
                  op_f=m
                  break
            original_input=op_f.inputs[0]
            print original_input
            input_x = sess.graph.get_tensor_by_name("input_1:0")
            print (input_x==original_input)
            # reload input_x as queue
            out_softmax = sess.graph.get_tensor_by_name("activation_58/truediv:0") 
            print out_softmax

            # img = cv2.imread(jpg_path, 0)

            from apps.pspnet.pkg.pspnet import pre_process
            from apps.pspnet.pkg.pspnet import utils   
            args_d={}
            args_d['panid']=""
            #pre_process.pre_process(namedtuple('Struct', args_d.keys())(*args_d.values()))         
            #inp=np.load 
            # img_out_softmax = sess.run(out_softmax,
            #                            feed_dict={input_x: 1.0 - np.array(img).reshape((-1,28, 28, 1)) / 255.0})

            # print "img_out_softmax:", img_out_softmax
            # prediction_labels = np.argmax(img_out_softmax, axis=1)
            # print "label:", prediction_labels


pb_path = './tensorflow_model/tensor_model.pb'
img = 'test/6/8_48.jpg'
recognize( pb_path)